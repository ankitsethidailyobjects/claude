from datetime import datetime, timedelta, timezone

from jobsearch.models import ATS, CompanyWatch
from jobsearch.sources import adzuna, ats, google_jobs
from jobsearch.sources.manual import make_job

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def company(kind):
    return CompanyWatch(name="Acme", ats=ATS(kind), slug="acme")


def test_greenhouse():
    j = ats.parse_greenhouse({
        "id": 11, "title": " Category Manager ", "location": {"name": "Gurugram, India"},
        "absolute_url": "https://x/11", "updated_at": "2026-10-10T10:00:00-04:00",
        "first_published": "2026-10-01T10:00:00Z", "content": "&lt;p&gt;Own the P&amp;amp;L&lt;/p&gt;",
    }, company("greenhouse"))
    assert j.source == "greenhouse:acme" and j.title == "Category Manager"
    assert j.posted_at == datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
    assert "Own the P&L" in j.description


def test_lever():
    j = ats.parse_lever({
        "id": "abc", "text": "Growth Lead", "categories": {"location": "Remote - India"},
        "hostedUrl": "https://jobs.lever.co/acme/abc", "createdAt": 1760000000000,
        "descriptionPlain": "About", "lists": [{"text": "You will", "content": "<li>grow</li>"}],
        "workplaceType": "remote",
    }, company("lever"))
    assert j.remote and "• grow" in j.description and j.posted_at.year == 2025


def test_ashby():
    j = ats.parse_ashby({
        "id": "z", "title": "PM", "location": "Bengaluru", "isRemote": False,
        "jobUrl": "https://jobs.ashbyhq.com/acme/z", "publishedAt": "2026-10-15T00:00:00.000+00:00",
        "descriptionPlain": "Build things",
    }, company("ashby"))
    assert j.url.endswith("/z") and j.posted_at.day == 15 and not j.remote


def test_google_jobs_parse():
    j = google_jobs.parse({
        "title": "Category Manager", "company_name": "Nykaa", "location": "Mumbai, Maharashtra, India",
        "via": "via LinkedIn", "description": "Desc",
        "job_highlights": [{"title": "Qualifications", "items": ["MBA"]}],
        "detected_extensions": {"posted_at": "2 days ago", "salary": "₹20–25 LPA"},
        "apply_options": [{"title": "LinkedIn", "link": "https://linkedin.com/jobs/1"}],
        "job_id": "eyJqb2IiOiIxIn0=",
    }, NOW)
    assert j.posted_at == NOW - timedelta(days=2)
    assert j.url == "https://linkedin.com/jobs/1" and "via LinkedIn" in j.posted_at_source
    assert "• MBA" in j.description and j.salary == "₹20–25 LPA"


def test_google_jobs_queries():
    assert google_jobs.build_queries(["PM"], ["Pune"], True) == ["PM in Pune", "PM remote India"]
    assert google_jobs.build_queries(["PM"], [], False) == ["PM in India"]


def test_adzuna_parse():
    j = adzuna.parse({
        "id": "42", "title": "Category Manager", "company": {"display_name": "Myntra"},
        "location": {"display_name": "Bangalore, Karnataka"}, "description": "snippet",
        "redirect_url": "https://adzuna/42", "created": "2026-10-16T08:00:00Z",
        "salary_min": 1800000, "salary_max": 2400000, "salary_is_predicted": "1",
    })
    assert j.company == "Myntra" and j.salary == "₹18–24 LPA (est.)" and j.posted_at.day == 16


def test_manual_requires_title_and_company():
    import pytest

    with pytest.raises(ValueError):
        make_job("", "Acme")
    assert make_job("PM", "Acme", url="https://x").external_id == "https://x"
