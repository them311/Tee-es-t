"""Shopify → HubSpot customer sync agent.

Pulls recent Shopify customers and upserts them into HubSpot so every order
becomes a qualified CRM contact automatically. Runs every hour by default.
"""

from __future__ import annotations

from snb.agents.base import Agent, AgentContext, AgentResult


class ShopifySyncAgent(Agent):
    name = "shopify_sync"
    interval_seconds: float = 3600.0

    async def run(self, ctx: AgentContext) -> AgentResult:
        try:
            from snb.integrations.hubspot import HubSpotClient
            from snb.integrations.shopify import ShopifyClient
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"missing dep: {e}")

        limit = int(ctx.params.get("limit", 50))
        try:
            shopify = ShopifyClient()
            hubspot = HubSpotClient()
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"integrations not configured: {e}")

        synced = 0
        failed = 0
        try:
            customers = await shopify.list_customers(limit=limit)
            for c in customers:
                email = c.get("email")
                if not email:
                    continue
                props = {
                    "email": email,
                    "firstname": c.get("first_name") or "",
                    "lastname": c.get("last_name") or "",
                    "phone": c.get("phone") or "",
                    "hs_analytics_source": "shopify",
                    "shopify_customer_id": str(c.get("id") or ""),
                }
                try:
                    await hubspot.upsert_contact(email, props)
                    synced += 1
                except Exception as e:  # noqa: BLE001
                    self.log.warning("upsert failed for {email}: {err}", email=email, err=str(e))
                    failed += 1
        finally:
            await shopify.aclose()
            await hubspot.aclose()

        return AgentResult(
            ok=failed == 0,
            data={"synced": synced, "failed": failed},
            metrics={"synced": synced, "failed": failed},
        )
