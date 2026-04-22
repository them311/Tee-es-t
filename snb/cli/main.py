"""Operator CLI — the canonical entrypoint for running ops tasks locally.

Usage:
    snb info
    snb agents list
    snb agents run <name> [--param k=v ...]
    snb scheduler
    snb integration ping <airtable|hubspot|shopify>
"""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from snb import __version__
from snb.agents.registry import registry
from snb.config import configure_logging, get_settings

app = typer.Typer(help="SNB operator CLI", no_args_is_help=True)
agents_app = typer.Typer(help="Agent management", no_args_is_help=True)
integration_app = typer.Typer(help="Integration sanity checks", no_args_is_help=True)
app.add_typer(agents_app, name="agents")
app.add_typer(integration_app, name="integration")


@app.callback()
def _root(verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False) -> None:
    s = get_settings()
    configure_logging(level="DEBUG" if verbose else s.log_level, json_mode=s.log_json)


@app.command()
def info() -> None:
    s = get_settings()
    typer.echo(f"snb {__version__}")
    typer.echo(f"env={s.env} debug={s.debug} log_level={s.log_level}")


@agents_app.command("list")
def agents_list() -> None:
    agents = registry.all()
    if not agents:
        typer.echo("(no agents registered)")
        return
    for a in agents:
        typer.echo(f"- {a.name}  interval={a.interval_seconds}")


@agents_app.command("run")
def agents_run(
    name: str,
    param: Annotated[list[str], typer.Option("--param", "-p", help="k=v")] = [],
) -> None:
    params = dict(p.split("=", 1) for p in param)
    result = asyncio.run(registry.run_one(name, **params))
    typer.echo(f"ok={result.ok} error={result.error}")
    if result.data is not None:
        typer.echo(f"data={result.data}")


@app.command()
def scheduler() -> None:
    """Run all scheduled agents forever."""
    asyncio.run(registry.run_scheduled())


@integration_app.command("ping")
def integration_ping(name: str) -> None:
    """Lightweight connectivity check for an integration."""

    async def _run() -> str:
        if name == "airtable":
            from snb.integrations.airtable import AirtableClient

            async with AirtableClient() as c:
                # Authenticated meta fetch — works even with zero tables listed.
                await c.http.get("/")
                return "airtable: reachable"
        if name == "hubspot":
            from snb.integrations.hubspot import HubSpotClient

            async with HubSpotClient() as c:
                await c.http.get("/crm/v3/objects/contacts", params={"limit": 1})
                return "hubspot: reachable"
        if name == "shopify":
            from snb.integrations.shopify import ShopifyClient

            async with ShopifyClient() as c:
                await c.http.get("/shop.json")
                return "shopify: reachable"
        raise typer.BadParameter(f"unknown integration '{name}'")

    typer.echo(asyncio.run(_run()))


if __name__ == "__main__":
    app()
