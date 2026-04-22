"""Notion API client — pages, databases, blocks."""

from __future__ import annotations

from typing import Any

from snb.config import get_settings
from snb.core.exceptions import AuthError
from snb.integrations.base import BaseIntegration

API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionClient(BaseIntegration):
    name = "notion"

    def __init__(self, token: str | None = None) -> None:
        s = get_settings().notion
        t = token or (s.token.get_secret_value() if s.token else None)
        if not t:
            raise AuthError("Notion requires NOTION_TOKEN")
        super().__init__(
            base_url=API_BASE,
            headers={
                "Authorization": f"Bearer {t}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

    async def query_database(
        self, database_id: str, *, filter_: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        body: dict[str, Any] = {}
        if filter_:
            body["filter"] = filter_
        payload = await self.http.post(f"/databases/{database_id}/query", json=body)
        return payload.get("results", [])

    async def create_page(self, parent: dict[str, Any], properties: dict[str, Any]) -> dict[str, Any]:
        return await self.http.post(
            "/pages", json={"parent": parent, "properties": properties}
        )

    async def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return await self.http.patch(f"/pages/{page_id}", json={"properties": properties})
