"""Shopify Admin API client (REST). Targets the versioned JSON endpoints.

Examples of usage:
    products, orders, customers, inventory, discounts — all follow the same
    GET /{api_version}/{resource}.json pattern.
"""

from __future__ import annotations

from typing import Any

from snb.config import get_settings
from snb.core.exceptions import AuthError
from snb.integrations.base import BaseIntegration


class ShopifyClient(BaseIntegration):
    name = "shopify"

    def __init__(
        self,
        shop_domain: str | None = None,
        access_token: str | None = None,
        api_version: str | None = None,
    ) -> None:
        s = get_settings().shopify
        domain = shop_domain or s.shop_domain
        token = access_token or (s.access_token.get_secret_value() if s.access_token else None)
        version = api_version or s.api_version
        if not domain or not token:
            raise AuthError("Shopify requires SHOPIFY_SHOP_DOMAIN and SHOPIFY_ACCESS_TOKEN")
        self.shop_domain = domain
        self.api_version = version
        super().__init__(
            base_url=f"https://{domain}/admin/api/{version}",
            headers={
                "X-Shopify-Access-Token": token,
                "Content-Type": "application/json",
            },
        )

    async def list_products(self, **params: Any) -> list[dict[str, Any]]:
        payload = await self.http.get("/products.json", params=params)
        return payload.get("products", [])

    async def list_orders(self, **params: Any) -> list[dict[str, Any]]:
        payload = await self.http.get("/orders.json", params=params)
        return payload.get("orders", [])

    async def list_customers(self, **params: Any) -> list[dict[str, Any]]:
        payload = await self.http.get("/customers.json", params=params)
        return payload.get("customers", [])

    async def create_product(self, product: dict[str, Any]) -> dict[str, Any]:
        return await self.http.post("/products.json", json={"product": product})
