"""Gmail client — OAuth2 refresh-token flow, send + search.

Intentionally minimal. Google's SDK is heavy; we only bring in what we need and
keep the integration swappable. For search/thread traversal, extend with the
v1 Users.messages endpoints as needed.
"""

from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Any

from snb.config import get_settings
from snb.core.exceptions import AuthError
from snb.core.http import AsyncHTTPClient
from snb.integrations.base import BaseIntegration

GMAIL_API = "https://gmail.googleapis.com/gmail/v1"
OAUTH_TOKEN = "https://oauth2.googleapis.com/token"


class GmailClient(BaseIntegration):
    name = "gmail"

    def __init__(
        self,
        sender: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        s = get_settings().gmail
        self.sender = sender or s.sender
        self.client_id = client_id or (s.client_id.get_secret_value() if s.client_id else None)
        self.client_secret = client_secret or (
            s.client_secret.get_secret_value() if s.client_secret else None
        )
        self.refresh_token = refresh_token or (
            s.refresh_token.get_secret_value() if s.refresh_token else None
        )
        if not all([self.sender, self.client_id, self.client_secret, self.refresh_token]):
            raise AuthError(
                "Gmail requires GMAIL_SENDER, GMAIL_CLIENT_ID, "
                "GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN"
            )
        super().__init__(base_url=GMAIL_API)
        self._access_token: str | None = None

    async def _refresh_access_token(self) -> str:
        async with AsyncHTTPClient() as oauth:
            payload = await oauth.post(
                OAUTH_TOKEN,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        token = payload.get("access_token")
        if not token:
            raise AuthError(f"gmail oauth refresh failed: {payload}")
        self._access_token = token
        self.http.default_headers["Authorization"] = f"Bearer {token}"
        # ensure in-flight client picks up the new header
        self.http._client.headers["Authorization"] = f"Bearer {token}"  # noqa: SLF001
        return token

    async def send(
        self, to: str, subject: str, body: str, *, html: bool = False
    ) -> dict[str, Any]:
        if not self._access_token:
            await self._refresh_access_token()
        msg = EmailMessage()
        msg["To"] = to
        msg["From"] = self.sender
        msg["Subject"] = subject
        if html:
            msg.set_content("(HTML message)")
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return await self.http.post(
            f"/users/{self.sender}/messages/send",
            json={"raw": raw},
        )
