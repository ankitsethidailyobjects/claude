import json
from datetime import datetime, timedelta, timezone

from sqlmodel import select

from jobsearch.models import Application, Job, JobSource, JobStatus, Liveness, SyncState
from jobsearch.normalize import NormalizedJob
from jobsearch.pipeline import (
    SourceReport,
    _pick_queries,
    age_days,
    archive_stale,
    mark_board_closures,
    upsert_jobs,
)

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def nj(source="google_jobs", ext="1", title="Category Manager", company="Acme Pvt Ltd",
       location="Gurgaon", posted_days=2, description="short"):
    return NormalizedJob(source=source, external_id=ext, title=title, company=company,
                         location=location, description=description,
                         posted_at=NOW - timedelta(days=posted_days) if posted_days is not None else None)


def test_new_job_then_same_source_updates_last_seen(session):
    r = SourceReport("x")
    upsert_jobs(session, [nj()], 21, r, NOW)
    upsert_jobs(session, [nj()], 21, r, NOW + timedelta(days=1))
    jobs = session.exec(select(Job)).all()
    assert len(jobs) == 1 and r.new == 1
    assert jobs[0].last_seen.replace(tzinfo=timezone.utc) == NOW + timedelta(days=1)


def test_cross_source_duplicate_merges(session):
    r = SourceReport("x")
    upsert_jobs(session, [nj(posted_days=2)], 21, r, NOW)
    upsert_jobs(session, [nj(source="adzuna", ext="a9", company="ACME", location="Gurugram, Haryana",
                             posted_days=5, description="much longer description")], 21, r, NOW)
    jobs = session.exec(select(Job)).all()
    assert len(jobs) == 1 and r.merged == 1
    assert jobs[0].description == "much longer description"
    assert age_days(jobs[0], NOW) == 5  # earliest posting date wins
    assert len(session.exec(select(JobSource)).all()) == 2


def test_too_old_jobs_are_not_stored(session):
    r = SourceReport("x")
    upsert_jobs(session, [nj(posted_days=40)], 21, r, NOW)
    assert r.too_old == 1 and session.exec(select(Job)).all() == []


def test_job_without_date_uses_first_seen(session):
    upsert_jobs(session, [nj(posted_days=None)], 21, SourceReport("x"), NOW)
    job = session.exec(select(Job)).one()
    assert age_days(job, NOW + timedelta(days=3)) == 3


def test_board_closures(session):
    src = "lever:acme"
    upsert_jobs(session, [nj(source=src, ext="a"), nj(source=src, ext="b", title="Growth Lead")],
                21, SourceReport("x"), NOW)
    closed = mark_board_closures(session, src, {"a"}, NOW)
    by_title = {j.title: j for j in session.exec(select(Job))}
    assert closed == 1
    assert by_title["Growth Lead"].liveness == Liveness.closed
    assert by_title["Category Manager"].liveness == Liveness.open


def test_archive_skips_tracked_jobs(session):
    upsert_jobs(session, [nj(ext="a"), nj(ext="b", title="Growth Lead")], 21, SourceReport("x"), NOW)
    tracked = session.exec(select(Job).where(Job.title == "Growth Lead")).one()
    session.add(Application(job_id=tracked.id))
    session.commit()
    assert archive_stale(session, 14, NOW + timedelta(days=15)) == 1
    statuses = {j.title: j.status for j in session.exec(select(Job))}
    assert statuses == {"Category Manager": JobStatus.archived, "Growth Lead": JobStatus.new}


def test_archived_job_comes_back_when_seen_again(session):
    upsert_jobs(session, [nj()], 21, SourceReport("x"), NOW)
    archive_stale(session, 14, NOW + timedelta(days=15))
    upsert_jobs(session, [nj()], 60, SourceReport("x"), NOW + timedelta(days=16))
    assert session.exec(select(Job)).one().status == JobStatus.new


def test_query_rotation_and_monthly_budget(session):
    qs = ["a", "b", "c", "d"]
    assert _pick_queries(session, "serpapi", qs, 3, 5, NOW) == ["a", "b", "c"]
    assert _pick_queries(session, "serpapi", qs, 3, 5, NOW) == ["d", "a"]  # budget: 2 left
    assert _pick_queries(session, "serpapi", qs, 3, 5, NOW) == []
    next_month = NOW + timedelta(days=20)
    assert _pick_queries(session, "serpapi", qs, 3, 5, next_month) == ["b", "c", "d"]
    assert json.loads(session.get(SyncState, "serpapi").cursor)["used"] == 3
