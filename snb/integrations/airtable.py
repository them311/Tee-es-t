"""Airtable client — minimal async wrapper over the REST API.

Covers the 90% path: list / create / update / delete records on a table.
Extend with views, filterByFormula, upserts when a concrete use case shows up.
"""

from __future__ import annotations

from typing import Any

from snb.config import get_settings
from snb.core.exceptions import AuthError
from snb.integrations.base import BaseIntegration

API_BASE = "https://api.airtable.com/v0"


class AirtableClient(BaseIntegration):
    name = "airtable"

    def __init__(self, base_id: str | None = None, api_key: str | None = None) -> None:
        s = get_settings().airtable
        key = api_key or (s.api_key.get_secret_value() if s.api_key else None)
        base = base_id or s.base_id
        if not key or not base:
            raise AuthError("Airtable requires AIRTABLE_API_KEY and AIRTABLE_BASE_ID")
        self.base_id = base
        super().__init__(
            base_url=f"{API_BASE}/{base}",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )

    async def list_records(
        self, table: str, *, page_size: int = 100, filter_formula: str | None = None
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        offset: str | None = None
        while True:
            params: dict[str, Any] = {"pageSize": page_size}
            if filter_formula:
                params["filterByFormula"] = filter_formula
            if offset:
                params["offset"] = offset
            payload = await self.http.get(f"/{table}", params=params)
            records.extend(payload.get("records", []))
            offset = payload.get("offset")
            if not offset:
                break
        return records

    async def create_record(self, table: str, fields: dict[str, Any]) -> dict[str, Any]:
        return await self.http.post(f"/{table}", json={"fields": fields})

    async def update_record(
        self, table: str, record_id: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.http.patch(f"/{table}/{record_id}", json={"fields": fields})

    async def delete_record(self, table: str, record_id: str) -> dict[str, Any]:
        return await self.http.delete(f"/{table}/{record_id}")
