"""Database tables."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ATS(str, Enum):
    greenhouse = "greenhouse"
    lever = "lever"
    ashby = "ashby"


class Liveness(str, Enum):
    open = "open"
    closed = "closed"
    unverified = "unverified"


class JobStatus(str, Enum):
    new = "new"
    hidden = "hidden"
    archived = "archived"


class Stage(str, Enum):
    saved = "saved"
    applied = "applied"
    interviewing = "interviewing"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"


class Profile(SQLModel, table=True):
    """Single row: the user's preferences and current resume."""

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = ""
    target_titles: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    seniority: str = ""
    years_experience: Optional[float] = None
    cities: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    remote_ok: bool = True
    min_ctc_lpa: Optional[float] = None
    must_have_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    deal_breakers: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    resume_filename: str = ""
    resume_text: str = ""
    # Short hash of resume + preferences; AI scores are cached per version.
    resume_version: str = ""
    updated_at: datetime = Field(default_factory=utcnow)


class CompanyWatch(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("ats", "slug"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ats: ATS
    slug: str
    active: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Normalised (company, title, location) hash used for dedupe across sources.
    dedupe_hash: str = Field(index=True, unique=True)
    title: str
    company: str
    location: str = ""
    remote: bool = False
    experience: str = ""
    salary: str = ""
    description: str = ""
    url: str = ""
    posted_at: Optional[datetime] = None
    posted_at_source: str = ""
    first_seen: datetime = Field(default_factory=utcnow)
    last_seen: datetime = Field(default_factory=utcnow)
    liveness: Liveness = Liveness.unverified
    liveness_checked_at: Optional[datetime] = None
    status: JobStatus = JobStatus.new


class JobSource(SQLModel, table=True):
    """Every place a job was seen (one job can arrive from several portals)."""

    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id", index=True)
    source: str
    external_id: str
    url: str = ""
    seen_at: datetime = Field(default_factory=utcnow)


class JobScore(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("job_id", "resume_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id", index=True)
    resume_version: str
    score: int
    analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow)


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id", unique=True)
    stage: Stage = Stage.saved
    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None
    notes: str = ""
    updated_at: datetime = Field(default_factory=utcnow)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id", index=True)
    kind: str  # "resume" | "cover_letter" | "pitch"
    content: str
    created_at: datetime = Field(default_factory=utcnow)


class RawEmail(SQLModel, table=True):
    """Alert emails are kept so parsers can be fixed and re-run."""

    id: Optional[int] = Field(default=None, primary_key=True)
    gmail_id: str = Field(index=True, unique=True)
    portal: str
    received_at: datetime
    subject: str = ""
    html: str = ""
    parsed_ok: bool = False


class SyncState(SQLModel, table=True):
    source: str = Field(primary_key=True)
    last_synced_at: Optional[datetime] = None
    cursor: str = ""  # e.g. Gmail history id
