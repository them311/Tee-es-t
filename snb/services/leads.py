"""Lead enrichment service.

Orchestrates: scrape raw leads -> normalize -> upsert to HubSpot + mirror to
Airtable. Kept simple and replaceable; each integration is injectable so tests
can mock them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from snb.config import get_logger

_log = get_logger("service.leads")


@dataclass
class Lead:
    email: str
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    source: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def to_hubspot_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"email": self.email}
        if self.first_name:
            props["firstname"] = self.first_name
        if self.last_name:
            props["lastname"] = self.last_name
        if self.company:
            props["company"] = self.company
        if self.source:
            props["hs_analytics_source"] = self.source
        return {**props, **self.extras}

    def to_airtable_fields(self) -> dict[str, Any]:
        return {
            "Email": self.email,
            "First Name": self.first_name or "",
            "Last Name": self.last_name or "",
            "Company": self.company or "",
            "Source": self.source or "",
            **self.extras,
        }


class LeadService:
    def __init__(self, *, hubspot: Any = None, airtable: Any = None, airtable_table: str = "Leads") -> None:
        self.hubspot = hubspot
        self.airtable = airtable
        self.airtable_table = airtable_table

    async def ingest(self, leads: list[Lead]) -> dict[str, int]:
        stats = {"hubspot": 0, "airtable": 0, "errors": 0}
        for lead in leads:
            try:
                if self.hubspot:
                    await self.hubspot.upsert_contact(lead.email, lead.to_hubspot_props())
                    stats["hubspot"] += 1
                if self.airtable:
                    await self.airtable.create_record(self.airtable_table, lead.to_airtable_fields())
                    stats["airtable"] += 1
            except Exception as e:  # noqa: BLE001
                _log.exception("lead ingest failed for {email}: {err}", email=lead.email, err=str(e))
                stats["errors"] += 1
        return stats
