"""FastAPI application.

Minimal CRUD needed to register a student and inspect matches. The API is
thin on purpose: the real value lives in the matching engine and agents.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from .config import get_settings
from .db import InMemoryRepository, Repository, SupabaseRepository
from .matching import rank_offers_for_student, rank_students_for_offer
from .models import ContractType, Offer, Source, Student

app = FastAPI(
    title="StudentFlow API",
    version="0.1.0",
    description="Real-time matching between student job offers and student profiles",
)


# ---- repository dependency ----


_repo_cache: Repository | None = None


def get_repository() -> Repository:
    """Return a Supabase repo if configured, else an in-memory one.

    The in-memory fallback lets you run the API locally without any external
    service — perfect for development and tests.
    """
    global _repo_cache
    if _repo_cache is not None:
        return _repo_cache
    settings = get_settings()
    if settings.supabase_configured:
        _repo_cache = SupabaseRepository(settings)
    else:
        _repo_cache = InMemoryRepository()
    return _repo_cache


# ---- request / response models ----


class StudentCreate(BaseModel):
    email: EmailStr
    full_name: str = ""
    city: str = ""
    remote_ok: bool = True
    skills: list[str] = Field(default_factory=list)
    accepted_contracts: list[ContractType] = Field(default_factory=list)
    max_hours_per_week: int = 20
    available_from: date | None = None
    available_until: date | None = None


class MatchOut(BaseModel):
    offer_id: UUID
    title: str
    company: str
    city: str
    score: float
    reasons: list[str]


class OfferCreate(BaseModel):
    """Body used when an employer publishes a mission through the web app."""

    title: str
    company: str
    description: str = ""
    city: str = ""
    remote: bool = False
    contract: ContractType = ContractType.PART_TIME
    hours_per_week: int | None = None
    skills: list[str] = Field(default_factory=list)
    url: str = ""
    contact_email: EmailStr | None = None


class StudentMatchOut(BaseModel):
    student_id: UUID
    full_name: str
    email: str
    city: str
    skills: list[str]
    score: float
    reasons: list[str]


# ---- routes ----


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/students", status_code=201)
def create_student(
    payload: StudentCreate, repo: Repository = Depends(get_repository)
) -> dict[str, str]:
    student = Student(**payload.model_dump())
    if hasattr(repo, "insert_student"):
        repo.insert_student(student)  # type: ignore[attr-defined]
    else:
        raise HTTPException(status_code=500, detail="Repository cannot insert students")
    return {"id": str(student.id)}


@app.get("/stats")
def stats(repo: Repository = Depends(get_repository)) -> dict[str, object]:
    """Lightweight aggregates for dashboards and ops health-checks."""
    return {
        "offers": repo.count_offers(),
        "students": repo.count_students(),
        "matches": repo.count_matches(),
        "matches_unnotified": repo.count_unnotified_matches(),
        "per_source": repo.count_offers_by_source(),
    }


@app.get("/students/{student_id}/matches", response_model=list[MatchOut])
def list_matches_for_student(
    student_id: UUID, repo: Repository = Depends(get_repository)
) -> list[MatchOut]:
    student = repo.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    offers = repo.list_recent_unmatched_offers()
    ranked = rank_offers_for_student(
        offers, student, threshold=get_settings().match_score_threshold
    )
    return [
        MatchOut(
            offer_id=offer.id,
            title=offer.title,
            company=offer.company,
            city=offer.city,
            score=result.score,
            reasons=result.reasons,
        )
        for offer, result in ranked
    ]


# ---- Company-facing routes ----------------------------------------------


@app.post("/offers", status_code=201)
def create_offer(
    payload: OfferCreate, repo: Repository = Depends(get_repository)
) -> dict[str, str]:
    """Employer publishes a mission.

    The offer is stored in the same `offers` table as scraped ones, so the
    MatcherAgent picks it up automatically on its next tick and notifies
    the best student candidates. Source is `studentjob` (manual entry) —
    `source_id` is derived from email+title so re-submits are idempotent.
    """
    source_id = f"manual:{(payload.contact_email or payload.company).lower()}:{payload.title}"
    offer = Offer(
        source=Source.STUDENTJOB,
        source_id=source_id,
        title=payload.title,
        description=payload.description,
        company=payload.company,
        city=payload.city,
        remote=payload.remote,
        contract=payload.contract,
        hours_per_week=payload.hours_per_week,
        skills=payload.skills,
        url=payload.url,
    )
    repo.upsert_offers([offer])
    return {"id": str(offer.id)}


@app.get("/offers/{offer_id}/matches", response_model=list[StudentMatchOut])
def list_matches_for_offer(
    offer_id: UUID, repo: Repository = Depends(get_repository)
) -> list[StudentMatchOut]:
    """Top students for a given mission, scored on the fly.

    Same engine as the student-side view — we just flip the axis. Employers
    get the best candidates ranked by score, with the reasons attached so
    they can explain why StudentFlow suggested them.
    """
    offer = repo.get_offer(offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    students = repo.list_active_students()
    ranked = rank_students_for_offer(
        offer, students, threshold=get_settings().match_score_threshold
    )
    return [
        StudentMatchOut(
            student_id=student.id,
            full_name=student.full_name,
            email=student.email,
            city=student.city,
            skills=student.skills,
            score=result.score,
            reasons=result.reasons,
        )
        for student, result in ranked
    ]
