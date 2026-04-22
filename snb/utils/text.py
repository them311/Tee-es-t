"""Text normalization helpers."""

from __future__ import annotations

import re
import unicodedata

_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = value.lower()
    value = _slug_re.sub("-", value).strip("-")
    return value


def normalize_email(email: str) -> str:
    return email.strip().lower()
