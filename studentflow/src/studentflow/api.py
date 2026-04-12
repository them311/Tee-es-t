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
from .matching import rank_offers_for_student
from .models import ContractType, Student

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


@app.get("/students/{student_id}/matches", response_model=list[MatchOut])
def list_matches_for_student(
    student_id: UUID, repo: Repository = Depends(get_repository)
) -> list[MatchOut]:
    students = {s.id: s for s in repo.list_active_students()}
    student = students.get(student_id)
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
