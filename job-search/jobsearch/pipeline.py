"""Fetch → normalise → freshness filter → dedupe/merge → store. Also closed-job and archive sweeps."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlmodel import Session, select

from jobsearch.config import Settings
from jobsearch.http import FetchError
from jobsearch.models import (
    Application,
    CompanyWatch,
    Job,
    JobSource,
    JobStatus,
    Liveness,
    SyncState,
    utcnow,
)
from jobsearch.normalize import NormalizedJob, as_utc, dedupe_hash
from jobsearch.profile import get_profile
from jobsearch.sources import adzuna, ats, google_jobs


@dataclass
class SourceReport:
    source: str
    fetched: int = 0
    new: int = 0
    merged: int = 0
    too_old: int = 0
    closed: int = 0
    error: str = ""


@dataclass
class RunReport:
    sources: list[SourceReport] = field(default_factory=list)
    archived: int = 0

    @property
    def new(self) -> int:
        return sum(s.new for s in self.sources)


def effective_posted(job: Job) -> datetime:
    return as_utc(job.posted_at) or as_utc(job.first_seen)


def age_days(job: Job, now: datetime | None = None) -> int:
    now = now or utcnow()
    return max(0, (now - effective_posted(job)).days)


def upsert_jobs(session: Session, jobs: list[NormalizedJob], max_age_days: int,
                report: SourceReport, now: datetime | None = None) -> set[str]:
    """Store jobs, merging duplicates. Returns external ids seen in this batch."""
    now = now or utcnow()
    cutoff = now - timedelta(days=max_age_days)
    seen: set[str] = set()
    for nj in jobs:
        if not nj.title or not nj.company:
            continue
        seen.add(nj.external_id)
        report.fetched += 1
        posted = as_utc(nj.posted_at)
        if posted and posted > now:
            posted = now
        link = session.exec(
            select(JobSource).where(JobSource.source == nj.source, JobSource.external_id == nj.external_id)
        ).first()
        job = session.get(Job, link.job_id) if link else None
        if job is None:
            job = session.exec(select(Job).where(Job.dedupe_hash == dedupe_hash(nj.company, nj.title, nj.location))).first()
        if job is None:
            if posted and posted < cutoff:
                report.too_old += 1
                continue
            job = Job(
                dedupe_hash=dedupe_hash(nj.company, nj.title, nj.location),
                title=nj.title, company=nj.company, location=nj.location, remote=nj.remote,
                experience=nj.experience, salary=nj.salary, description=nj.description, url=nj.url,
                posted_at=posted, posted_at_source=nj.posted_at_source, first_seen=now, last_seen=now,
            )
            session.add(job)
            session.flush()
            report.new += 1
        else:
            _merge(job, nj, posted, now)
            if not link:
                report.merged += 1
        if link is None:
            session.add(JobSource(job_id=job.id, source=nj.source, external_id=nj.external_id, url=nj.url, seen_at=now))
        else:
            link.seen_at = now
            session.add(link)
    session.commit()
    return seen


def _merge(job: Job, nj: NormalizedJob, posted: datetime | None, now: datetime) -> None:
    job.last_seen = now
    if len(nj.description) > len(job.description):
        job.description = nj.description
    for attr in ("salary", "experience", "location"):
        if not getattr(job, attr) and getattr(nj, attr):
            setattr(job, attr, getattr(nj, attr))
    if not job.url and nj.url:
        job.url = nj.url
    job.remote = job.remote or nj.remote
    # Keep the earliest credible posting date across sources.
    if posted and (job.posted_at is None or posted < as_utc(job.posted_at)):
        job.posted_at, job.posted_at_source = posted, nj.posted_at_source
    if job.status == JobStatus.archived:
        job.status = JobStatus.new


def mark_board_closures(session: Session, source: str, seen_ids: set[str], now: datetime | None = None) -> int:
    """A company board is complete, so a job missing from it has been taken down."""
    now = now or utcnow()
    closed = 0
    for link in session.exec(select(JobSource).where(JobSource.source == source)):
        job = session.get(Job, link.job_id)
        if job is None:
            continue
        if link.external_id in seen_ids:
            job.liveness = Liveness.open
        elif job.liveness != Liveness.closed:
            job.liveness = Liveness.closed
            closed += 1
        job.liveness_checked_at = now
        session.add(job)
    session.commit()
    return closed


def archive_stale(session: Session, archive_after_days: int, now: datetime | None = None) -> int:
    now = now or utcnow()
    cutoff = now - timedelta(days=archive_after_days)
    tracked = set(session.exec(select(Application.job_id)))
    count = 0
    for job in session.exec(select(Job).where(Job.status == JobStatus.new)):
        if job.id not in tracked and as_utc(job.last_seen) < cutoff:
            job.status = JobStatus.archived
            session.add(job)
            count += 1
    session.commit()
    return count


def _get_state(session: Session, source: str) -> SyncState:
    return session.get(SyncState, source) or SyncState(source=source)


def _pick_queries(session: Session, source: str, queries: list[str], per_run: int,
                  monthly_limit: int, now: datetime) -> list[str]:
    """Rotate through queries across runs while staying under a monthly API budget."""
    state = _get_state(session, source)
    cur = json.loads(state.cursor or "{}")
    month = now.strftime("%Y-%m")
    if cur.get("month") != month:
        cur = {"month": month, "used": 0, "next": cur.get("next", 0)}
    room = max(0, min(per_run, monthly_limit - cur["used"]))
    if not queries or room == 0:
        return []
    start = cur["next"] % len(queries)
    picked = [queries[(start + i) % len(queries)] for i in range(min(room, len(queries)))]
    cur["used"] += len(picked)
    cur["next"] = start + len(picked)
    state.cursor = json.dumps(cur)
    state.last_synced_at = now
    session.add(state)
    session.commit()
    return picked


def fetch_all(session: Session, settings: Settings, now: datetime | None = None) -> RunReport:
    now = now or utcnow()
    report = RunReport()
    profile = get_profile(session)

    for company in session.exec(select(CompanyWatch).where(CompanyWatch.active == True)):  # noqa: E712
        r = SourceReport(source=f"{company.name} ({company.ats.value})")
        report.sources.append(r)
        try:
            jobs = ats.fetch_company(company)
        except (FetchError, KeyError, TypeError, ValueError) as e:
            r.error = str(e)
            continue
        seen = upsert_jobs(session, jobs, settings.max_job_age_days, r, now)
        r.closed = mark_board_closures(session, ats.source_name(company), seen, now)

    if settings.serpapi_key and profile.target_titles:
        r = SourceReport(source="Google Jobs (SerpAPI)")
        report.sources.append(r)
        queries = google_jobs.build_queries(profile.target_titles, profile.cities, profile.remote_ok)
        for q in _pick_queries(session, "serpapi", queries, settings.serpapi_queries_per_run,
                               settings.serpapi_monthly_limit, now):
            try:
                upsert_jobs(session, google_jobs.search(settings.serpapi_key, q, now),
                            settings.max_job_age_days, r, now)
            except (FetchError, RuntimeError) as e:
                r.error = f"{q}: {e}"

    if settings.adzuna_app_id and settings.adzuna_app_key and profile.target_titles:
        r = SourceReport(source="Adzuna")
        report.sources.append(r)
        wheres = profile.cities or [""]
        pairs = [(t, w) for t in profile.target_titles for w in wheres][:10]
        for what, where in pairs:
            try:
                jobs = adzuna.search(settings.adzuna_app_id, settings.adzuna_app_key, what, where,
                                     max_days_old=settings.max_job_age_days)
                upsert_jobs(session, jobs, settings.max_job_age_days, r, now)
            except FetchError as e:
                r.error = f"{what} / {where or 'India'}: {e}"
                if e.status in (401, 403):
                    break

    report.archived = archive_stale(session, settings.archive_after_days, now)
    return report
