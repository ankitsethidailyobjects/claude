"""Company watchlist: careers pages hosted on Greenhouse, Lever or Ashby."""

import json
import re
import urllib.error
import urllib.request
from urllib.parse import urlparse

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from jobsearch.models import ATS, CompanyWatch

# Public, unauthenticated job-board APIs.
BOARD_API = {
    ATS.greenhouse: "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    ATS.lever: "https://api.lever.co/v0/postings/{slug}?mode=json",
    ATS.ashby: "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}

_HOSTS = {
    "boards.greenhouse.io": ATS.greenhouse,
    "job-boards.greenhouse.io": ATS.greenhouse,
    "boards.eu.greenhouse.io": ATS.greenhouse,
    "job-boards.eu.greenhouse.io": ATS.greenhouse,
    "boards-api.greenhouse.io": ATS.greenhouse,
    "jobs.lever.co": ATS.lever,
    "jobs.eu.lever.co": ATS.lever,
    "api.lever.co": ATS.lever,
    "jobs.ashbyhq.com": ATS.ashby,
    "api.ashbyhq.com": ATS.ashby,
}

_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class WatchlistError(ValueError):
    pass


class BoardNotFound(WatchlistError):
    pass


def parse_careers_url(url: str) -> tuple[ATS, str]:
    """Turn a careers-page URL into (ats, slug).

    e.g. https://jobs.lever.co/cred/abc → (lever, "cred")
    """
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    ats = _HOSTS.get(host)
    if ats is None:
        raise WatchlistError(
            f"{host or url} is not a Greenhouse, Lever or Ashby careers page. "
            "Check the company's 'Careers' link — it often redirects to one of these."
        )
    parts = [p for p in parsed.path.split("/") if p]
    # API URLs carry a prefix before the slug.
    if host == "boards-api.greenhouse.io" and parts[:2] == ["v1", "boards"]:
        parts = parts[2:]
    elif host == "api.lever.co" and parts[:2] == ["v0", "postings"]:
        parts = parts[2:]
    elif host == "api.ashbyhq.com" and parts[:2] == ["posting-api", "job-board"]:
        parts = parts[2:]
    elif host.endswith("greenhouse.io") and parts[:1] == ["embed"]:
        # boards.greenhouse.io/embed/job_board?for=slug
        query = dict(p.split("=", 1) for p in parsed.query.split("&") if "=" in p)
        parts = [query["for"]] if "for" in query else []
    if not parts or not _SLUG_RE.match(parts[0]):
        raise WatchlistError(f"Could not find the company name in {url}")
    return ats, parts[0].lower()


def add_company(session: Session, name: str, ats: ATS | str, slug: str) -> CompanyWatch:
    ats = ATS(ats)
    slug = slug.strip().lower()
    if not name.strip():
        raise WatchlistError("Company name is required")
    if not _SLUG_RE.match(slug):
        raise WatchlistError(f"Invalid board name: {slug!r}")
    company = CompanyWatch(name=name.strip(), ats=ats, slug=slug)
    session.add(company)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise WatchlistError(f"{ats.value}/{slug} is already on the watchlist") from None
    session.refresh(company)
    return company


def list_companies(session: Session, active_only: bool = False) -> list[CompanyWatch]:
    query = select(CompanyWatch).order_by(CompanyWatch.name)
    if active_only:
        query = query.where(CompanyWatch.active == True)  # noqa: E712
    return list(session.exec(query))


def set_active(session: Session, company_id: int, active: bool) -> None:
    company = session.get(CompanyWatch, company_id)
    if company:
        company.active = active
        session.add(company)
        session.commit()


def remove_company(session: Session, company_id: int) -> None:
    company = session.get(CompanyWatch, company_id)
    if company:
        session.delete(company)
        session.commit()


def fetch_board(ats: ATS | str, slug: str, timeout: float = 15) -> list[dict]:
    """Fetch the raw job list from a company's public board."""
    ats = ATS(ats)
    url = BOARD_API[ats].format(slug=slug)
    req = urllib.request.Request(url, headers={"User-Agent": "jobsearch/0.1 (personal use)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise BoardNotFound(f"No {ats.value} board named {slug!r}") from None
        raise WatchlistError(f"{ats.value} returned HTTP {e.code}") from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise WatchlistError(f"Could not reach {ats.value}: {e}") from None
    if ats is ATS.lever:
        return data if isinstance(data, list) else []
    return data.get("jobs", []) if isinstance(data, dict) else []
