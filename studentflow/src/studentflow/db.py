"""Repository layer on top of Supabase.

The concrete Supabase client is only imported when actually needed so that
tests and local development can run without the package installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from .config import Settings, get_settings
from .models import Match, Offer, Student

if TYPE_CHECKING:
    from supabase import Client


class Repository(Protocol):
    def upsert_offers(self, offers: list[Offer]) -> int: ...
    def list_active_students(self) -> list[Student]: ...
    def list_recent_unmatched_offers(self, limit: int = 200) -> list[Offer]: ...
    def insert_match(self, match: Match) -> None: ...
    def list_unnotified_matches(self, limit: int = 100) -> list[Match]: ...
    def mark_match_notified(self, match_id: UUID) -> None: ...


class SupabaseRepository:
    """Thin wrapper around the Supabase Python client."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        if self._client is None:
            if not self._settings.supabase_configured:
                raise RuntimeError(
                    "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY."
                )
            from supabase import create_client

            self._client = create_client(
                self._settings.supabase_url,
                self._settings.supabase_service_key,
            )
        return self._client

    # ---- offers ----

    def upsert_offers(self, offers: list[Offer]) -> int:
        if not offers:
            return 0
        rows = [_offer_to_row(o) for o in offers]
        self.client.table("offers").upsert(rows, on_conflict="source,source_id").execute()
        return len(rows)

    def list_recent_unmatched_offers(self, limit: int = 200) -> list[Offer]:
        resp = (
            self.client.table("offers")
            .select("*")
            .order("scraped_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_row_to_offer(r) for r in (resp.data or [])]

    # ---- students ----

    def list_active_students(self) -> list[Student]:
        resp = self.client.table("students").select("*").eq("active", True).execute()
        return [_row_to_student(r) for r in (resp.data or [])]

    def insert_student(self, student: Student) -> None:
        self.client.table("students").insert(_student_to_row(student)).execute()

    # ---- matches ----

    def insert_match(self, match: Match) -> None:
        self.client.table("matches").insert(_match_to_row(match)).execute()

    def list_unnotified_matches(self, limit: int = 100) -> list[Match]:
        resp = (
            self.client.table("matches").select("*").is_("notified_at", None).limit(limit).execute()
        )
        return [_row_to_match(r) for r in (resp.data or [])]

    def mark_match_notified(self, match_id: UUID) -> None:
        from datetime import datetime

        self.client.table("matches").update({"notified_at": datetime.utcnow().isoformat()}).eq(
            "id", str(match_id)
        ).execute()


# ---- row adapters ----
# These live at module level so they can be imported and tested standalone.


def _offer_to_row(o: Offer) -> dict[str, Any]:
    return {
        "id": str(o.id),
        "source": o.source.value,
        "source_id": o.source_id,
        "title": o.title,
        "description": o.description,
        "company": o.company,
        "city": o.city,
        "remote": o.remote,
        "contract": o.contract.value,
        "hours_per_week": o.hours_per_week,
        "skills": o.skills,
        "starts_on": o.starts_on.isoformat() if o.starts_on else None,
        "ends_on": o.ends_on.isoformat() if o.ends_on else None,
        "url": o.url,
        "scraped_at": o.scraped_at.isoformat(),
    }


def _row_to_offer(row: dict[str, Any]) -> Offer:
    return Offer.model_validate(row)


def _student_to_row(s: Student) -> dict[str, Any]:
    return {
        "id": str(s.id),
        "email": s.email,
        "full_name": s.full_name,
        "city": s.city,
        "remote_ok": s.remote_ok,
        "skills": s.skills,
        "accepted_contracts": [c.value for c in s.accepted_contracts],
        "max_hours_per_week": s.max_hours_per_week,
        "available_from": s.available_from.isoformat() if s.available_from else None,
        "available_until": s.available_until.isoformat() if s.available_until else None,
        "active": s.active,
    }


def _row_to_student(row: dict[str, Any]) -> Student:
    return Student.model_validate(row)


def _match_to_row(m: Match) -> dict[str, Any]:
    return {
        "id": str(m.id),
        "offer_id": str(m.offer_id),
        "student_id": str(m.student_id),
        "score": m.score,
        "reasons": m.reasons,
        "created_at": m.created_at.isoformat(),
        "notified_at": m.notified_at.isoformat() if m.notified_at else None,
    }


def _row_to_match(row: dict[str, Any]) -> Match:
    return Match.model_validate(row)


class InMemoryRepository:
    """Repository used for local dev and tests. No external deps."""

    def __init__(self) -> None:
        self.offers: dict[tuple[str, str], Offer] = {}
        self.students: dict[UUID, Student] = {}
        self.matches: dict[UUID, Match] = {}

    def upsert_offers(self, offers: list[Offer]) -> int:
        for o in offers:
            self.offers[(o.source.value, o.source_id)] = o
        return len(offers)

    def list_active_students(self) -> list[Student]:
        return [s for s in self.students.values() if s.active]

    def list_recent_unmatched_offers(self, limit: int = 200) -> list[Offer]:
        return list(self.offers.values())[-limit:]

    def insert_student(self, student: Student) -> None:
        self.students[student.id] = student

    def insert_match(self, match: Match) -> None:
        self.matches[match.id] = match

    def list_unnotified_matches(self, limit: int = 100) -> list[Match]:
        return [m for m in self.matches.values() if m.notified_at is None][:limit]

    def mark_match_notified(self, match_id: UUID) -> None:
        from datetime import datetime

        m = self.matches.get(match_id)
        if m is not None:
            m.notified_at = datetime.utcnow()
