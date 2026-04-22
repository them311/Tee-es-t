from __future__ import annotations

from snb.utils.text import normalize_email, slugify


def test_slugify_basic() -> None:
    assert slugify("La Française des Sauces") == "la-francaise-des-sauces"
    assert slugify("  Hello — World  ") == "hello-world"


def test_normalize_email() -> None:
    assert normalize_email("  FOO@BAR.com ") == "foo@bar.com"
