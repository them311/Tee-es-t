"""HubSpot CRM client — contacts/companies/deals over the v3 CRM API.

Auth uses a Private App access token. Rate limiting is handled by the
AsyncHTTPClient retry layer.
"""

from __future__ import annotations

from typing import Any

from snb.config import get_settings
from snb.core.exceptions import AuthError
from snb.integrations.base import BaseIntegration

API_BASE = "https://api.hubapi.com"


class HubSpotClient(BaseIntegration):
    name = "hubspot"

    def __init__(self, access_token: str | None = None) -> None:
        s = get_settings().hubspot
        token = access_token or (s.access_token.get_secret_value() if s.access_token else None)
        if not token:
            raise AuthError("HubSpot requires HUBSPOT_ACCESS_TOKEN")
        super().__init__(
            base_url=API_BASE,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

    async def search(
        self, object_type: str, *, filter_groups: list[dict[str, Any]], limit: int = 100
    ) -> list[dict[str, Any]]:
        payload = await self.http.post(
            f"/crm/v3/objects/{object_type}/search",
            json={"filterGroups": filter_groups, "limit": limit},
        )
        return payload.get("results", [])

    async def create(self, object_type: str, properties: dict[str, Any]) -> dict[str, Any]:
        return await self.http.post(
            f"/crm/v3/objects/{object_type}", json={"properties": properties}
        )

    async def update(
        self, object_type: str, object_id: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.http.patch(
            f"/crm/v3/objects/{object_type}/{object_id}", json={"properties": properties}
        )

    async def get(self, object_type: str, object_id: str) -> dict[str, Any]:
        return await self.http.get(f"/crm/v3/objects/{object_type}/{object_id}")

    async def upsert_contact(self, email: str, properties: dict[str, Any]) -> dict[str, Any]:
        existing = await self.search(
            "contacts",
            filter_groups=[
                {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
            ],
            limit=1,
        )
        props = {**properties, "email": email}
        if existing:
            return await self.update("contacts", existing[0]["id"], props)
        return await self.create("contacts", props)
