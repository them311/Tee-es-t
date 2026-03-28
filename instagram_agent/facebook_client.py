"""Facebook Graph API client for Instagram Business API access."""

import logging
import time

import requests

from .config import FacebookCredentials

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookAPIError(Exception):
    def __init__(self, message: str, code: int = 0, subcode: int = 0):
        super().__init__(message)
        self.code = code
        self.subcode = subcode


class FacebookClient:
    """Handles authentication and raw API calls to Facebook Graph API."""

    def __init__(self, credentials: FacebookCredentials):
        self.credentials = credentials
        self.session = requests.Session()
        self.session.params = {"access_token": credentials.access_token}

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{GRAPH_API_BASE}/{endpoint}"
        retries = 3
        for attempt in range(retries):
            try:
                resp = self.session.request(method, url, **kwargs)
                data = resp.json()

                if "error" in data:
                    err = data["error"]
                    code = err.get("code", 0)
                    # Rate limit - wait and retry
                    if code == 4 or code == 32:
                        wait = min(60 * (2 ** attempt), 300)
                        logger.warning(f"Rate limited. Waiting {wait}s before retry...")
                        time.sleep(wait)
                        continue
                    raise FacebookAPIError(
                        err.get("message", "Unknown error"),
                        code=code,
                        subcode=err.get("error_subcode", 0),
                    )
                return data

            except requests.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise FacebookAPIError(f"Network error: {e}")

        raise FacebookAPIError("Max retries exceeded")

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        return self._request("GET", endpoint, params=params or {})

    def post(self, endpoint: str, data: dict | None = None) -> dict:
        return self._request("POST", endpoint, data=data or {})

    def verify_token(self) -> dict:
        """Verify the access token is valid and get token info."""
        return self.get("me", params={"fields": "id,name"})

    def get_long_lived_token(self) -> str:
        """Exchange a short-lived token for a long-lived one."""
        data = self.get("oauth/access_token", params={
            "grant_type": "fb_exchange_token",
            "client_id": self.credentials.app_id,
            "client_secret": self.credentials.app_secret,
            "fb_exchange_token": self.credentials.access_token,
        })
        return data.get("access_token", "")
