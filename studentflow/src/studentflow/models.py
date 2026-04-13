"""Pydantic domain models.

These models are the ground truth for every boundary of the system: scrapers
return them, the matching engine consumes them, the API serializes them, and
the DB layer persists them. Keep them dumb — no I/O, no business rules beyond
validation.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ContractType(StrEnum):
    INTERNSHIP = "internship"  # stage
    APPRENTICESHIP = "apprenticeship"  # alternance
    CDD = "cdd"
    CDI = "cdi"
    PART_TIME = "part_time"  # job étudiant
    FREELANCE = "freelance"
    OTHER = "other"


class Source(StrEnum):
    FRANCE_TRAVAIL = "france_travail"
    INDEED = "indeed"
    HELLOWORK = "hellowork"
    STUDENTJOB = "studentjob"
    JOBTEASER = "jobteaser"
    ADZUNA = "adzuna"
    JOOBLE = "jooble"


def _norm_skills(skills: list[str]) -> list[str]:
    """Lowercase + strip + dedupe while preserving insertion order."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in skills:
        s = raw.strip().lower()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


class Offer(BaseModel):
    model_config = ConfigDict(frozen=False)

    id: UUID = Field(default_factory=uuid4)
    source: Source
    source_id: str  # unique within (source, source_id)
    title: str
    description: str = ""
    company: str = ""
    city: str = ""
    remote: bool = False
    contract: ContractType = ContractType.OTHER
    hours_per_week: int | None = None
    skills: list[str] = Field(default_factory=list)
    starts_on: date | None = None
    ends_on: date | None = None
    url: str = ""
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    def model_post_init(self, _: object) -> None:
        object.__setattr__(self, "skills", _norm_skills(self.skills))
        object.__setattr__(self, "city", self.city.strip().lower())


class Student(BaseModel):
    model_config = ConfigDict(frozen=False)

    id: UUID = Field(default_factory=uuid4)
    email: str
    full_name: str = ""
    city: str = ""
    remote_ok: bool = True
    skills: list[str] = Field(default_factory=list)
    accepted_contracts: list[ContractType] = Field(default_factory=list)
    max_hours_per_week: int = 20
    available_from: date | None = None
    available_until: date | None = None
    active: bool = True

    def model_post_init(self, _: object) -> None:
        object.__setattr__(self, "skills", _norm_skills(self.skills))
        object.__setattr__(self, "city", self.city.strip().lower())


class MatchResult(BaseModel):
    """Output of the matching engine. Not persisted as-is."""

    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    components: dict[str, float] = Field(default_factory=dict)


class Match(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    offer_id: UUID
    student_id: UUID
    score: float
    reasons: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notified_at: datetime | None = None


class Notification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    match_id: UUID
    channel: str = "webhook"
    payload: dict[str, object] = Field(default_factory=dict)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    succeeded: bool = True
    error: str | None = None
