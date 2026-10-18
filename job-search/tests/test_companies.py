import pytest

from jobsearch.companies import (
    WatchlistError,
    add_company,
    list_companies,
    parse_careers_url,
    remove_company,
    set_active,
)
from jobsearch.models import ATS


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://jobs.lever.co/cred", (ATS.lever, "cred")),
        ("jobs.lever.co/Cred/3f1a-apply", (ATS.lever, "cred")),
        ("https://boards.greenhouse.io/phonepe/jobs/123", (ATS.greenhouse, "phonepe")),
        ("https://job-boards.greenhouse.io/groww", (ATS.greenhouse, "groww")),
        ("https://boards.greenhouse.io/embed/job_board?for=zepto", (ATS.greenhouse, "zepto")),
        ("https://boards-api.greenhouse.io/v1/boards/meesho/jobs", (ATS.greenhouse, "meesho")),
        ("https://jobs.ashbyhq.com/sarvam", (ATS.ashby, "sarvam")),
        ("https://api.lever.co/v0/postings/cred?mode=json", (ATS.lever, "cred")),
    ],
)
def test_parse_careers_url(url, expected):
    assert parse_careers_url(url) == expected


@pytest.mark.parametrize("url", ["https://www.naukri.com/foo", "https://jobs.lever.co/", "not a url"])
def test_parse_careers_url_rejects(url):
    with pytest.raises(WatchlistError):
        parse_careers_url(url)


def test_watchlist_crud(session):
    c = add_company(session, "CRED", "lever", "CRED")
    assert c.slug == "cred"
    with pytest.raises(WatchlistError):
        add_company(session, "Cred again", ATS.lever, "cred")
    add_company(session, "Groww", ATS.greenhouse, "groww")
    set_active(session, c.id, False)
    assert [x.name for x in list_companies(session, active_only=True)] == ["Groww"]
    remove_company(session, c.id)
    assert [x.name for x in list_companies(session)] == ["Groww"]


def test_fetch_board_404_is_board_not_found(monkeypatch):
    import urllib.error

    from jobsearch import companies

    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr(companies.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(companies.BoardNotFound):
        companies.fetch_board("lever", "nope")


def test_fetch_board_shapes(monkeypatch):
    import io
    import json

    from jobsearch import companies

    payloads = {"lever": [{"id": 1}], "greenhouse": {"jobs": [{"id": 1}, {"id": 2}]}}

    def fake_urlopen(req, timeout):
        key = "lever" if "lever" in req.full_url else "greenhouse"
        return io.BytesIO(json.dumps(payloads[key]).encode())

    monkeypatch.setattr(companies.urllib.request, "urlopen", fake_urlopen)
    assert len(companies.fetch_board("lever", "x")) == 1
    assert len(companies.fetch_board("greenhouse", "x")) == 2
