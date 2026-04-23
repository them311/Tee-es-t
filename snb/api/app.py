"""FastAPI app factory.

Exposes:
- GET  /health               -> liveness + version + env
- POST /webhook/lead         -> ingest a new lead (Airtable + HubSpot)
- POST /webhook/shopify      -> ingest a Shopify order (mirror customer to CRM)
- POST /agents/{name}/run    -> kick off an agent out-of-band (API-key gated)

Everything is bootstrapped through ``snb.bootstrap`` so agents are registered
before routes are wired.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from snb import __version__
from snb.agents.base import AgentContext
from snb.agents.registry import registry
from snb.config import configure_logging, get_logger, get_settings
from snb.services.leads import Lead, LeadService

_log = get_logger("api")


def _require_api_key(provided: str | None) -> None:
    expected = os.getenv("SNB_API_KEY")
    if not expected:
        return  # open mode for dev
    if provided != expected:
        raise HTTPException(status_code=401, detail="invalid api key")


def create_app() -> FastAPI:
    # Register all built-in agents before the app answers any request.
    import snb.bootstrap  # noqa: F401

    settings = get_settings()
    configure_logging(level=settings.log_level, json_mode=settings.log_json)

    app = FastAPI(
        title="SNB API",
        version=__version__,
        description="Operational automation surface for SNB Consulting / LFDS.",
    )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "ok": True,
            "service": "snb",
            "version": __version__,
            "env": settings.env,
            "agents": [a.name for a in registry.all()],
        }

    @app.post("/webhook/lead")
    async def webhook_lead(request: Request) -> dict[str, Any]:
        payload = await request.json()
        email = payload.get("email")
        if not email:
            raise HTTPException(422, detail="email is required")
        lead = Lead(
            email=email,
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            company=payload.get("company"),
            source=payload.get("source") or "webhook",
            extras=payload.get("extras") or {},
        )
        hubspot = await _maybe("hubspot")
        airtable = await _maybe("airtable")
        service = LeadService(hubspot=hubspot, airtable=airtable)
        try:
            stats = await service.ingest([lead])
        finally:
            if hubspot:
                await hubspot.aclose()
            if airtable:
                await airtable.aclose()
        return {"ok": True, "stats": stats}

    @app.post("/webhook/shopify")
    async def webhook_shopify(request: Request) -> dict[str, Any]:
        payload = await request.json()
        customer = payload.get("customer") or {}
        email = customer.get("email")
        if not email:
            raise HTTPException(422, detail="customer.email is required")
        lead = Lead(
            email=email,
            first_name=customer.get("first_name"),
            last_name=customer.get("last_name"),
            source="shopify",
            extras={
                "shopify_order_id": payload.get("id"),
                "total_price": payload.get("total_price"),
            },
        )
        hubspot = await _maybe("hubspot")
        try:
            if hubspot:
                await hubspot.upsert_contact(email, lead.to_hubspot_props())
        finally:
            if hubspot:
                await hubspot.aclose()
        return {"ok": True}

    @app.post("/agents/{name}/run")
    async def agents_run(
        name: str,
        request: Request,
        x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
    ) -> dict[str, Any]:
        _require_api_key(x_api_key)
        params: dict[str, Any] = {}
        if request.headers.get("content-length", "0") != "0":
            params = await request.json()
        result = await registry.run_one(name, **params)
        return {
            "ok": result.ok,
            "error": result.error,
            "data": result.data,
            "metrics": result.metrics,
        }

    return app


async def _maybe(name: str) -> Any:
    """Instantiate an integration only if its credentials are configured.

    Returns None if env vars are missing — routes degrade gracefully rather
    than hard-failing in environments where only a subset of integrations is
    wired.
    """
    try:
        if name == "hubspot":
            from snb.integrations.hubspot import HubSpotClient

            return HubSpotClient()
        if name == "airtable":
            from snb.integrations.airtable import AirtableClient

            return AirtableClient()
    except Exception as e:  # noqa: BLE001
        _log.warning("integration {n} unavailable: {err}", n=name, err=str(e))
    return None


# Uvicorn entrypoint: ``uvicorn snb.api.app:app``
app = create_app()
