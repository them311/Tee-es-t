"""Lead enrichment agent.

Reads leads from an Airtable table, looks them up in HubSpot, and pushes
back any missing properties. Keeps the two systems in sync in one direction
(Airtable → HubSpot) — safer default to avoid write loops.
"""

from __future__ import annotations

from snb.agents.base import Agent, AgentContext, AgentResult


class LeadEnrichmentAgent(Agent):
    name = "lead_enrichment"
    interval_seconds: float = 900.0  # 15 min

    async def run(self, ctx: AgentContext) -> AgentResult:
        try:
            from snb.integrations.airtable import AirtableClient
            from snb.integrations.hubspot import HubSpotClient
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"missing dep: {e}")

        table = ctx.params.get("table", "Leads")
        filter_formula = ctx.params.get(
            "filter_formula", "NOT({Synced HubSpot})"
        )

        try:
            airtable = AirtableClient()
            hubspot = HubSpotClient()
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"integrations not configured: {e}")

        enriched = 0
        failed = 0
        try:
            records = await airtable.list_records(table, filter_formula=filter_formula)
            for rec in records:
                fields = rec.get("fields", {})
                email = fields.get("Email") or fields.get("email")
                if not email:
                    continue
                props = {
                    "email": email,
                    "firstname": fields.get("First Name") or "",
                    "lastname": fields.get("Last Name") or "",
                    "company": fields.get("Company") or "",
                    "hs_analytics_source": fields.get("Source") or "airtable",
                }
                try:
                    await hubspot.upsert_contact(email, props)
                    await airtable.update_record(
                        table, rec["id"], {"Synced HubSpot": True}
                    )
                    enriched += 1
                except Exception as e:  # noqa: BLE001
                    self.log.warning("enrich failed {email}: {err}", email=email, err=str(e))
                    failed += 1
        finally:
            await airtable.aclose()
            await hubspot.aclose()

        return AgentResult(
            ok=failed == 0,
            data={"enriched": enriched, "failed": failed},
            metrics={"enriched": enriched, "failed": failed},
        )
