"""Adzuna India search API (free key: developer.adzuna.com)."""

from jobsearch.http import get_json
from jobsearch.normalize import NormalizedJob, format_lpa, looks_remote, parse_iso

SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"


def search(app_id: str, app_key: str, what: str, where: str = "", max_days_old: int = 21,
           results: int = 50) -> list[NormalizedJob]:
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": what,
        "results_per_page": results,
        "max_days_old": max_days_old,
        "sort_by": "date",
        "content-type": "application/json",
    }
    if where:
        params["where"] = where
    data = get_json(SEARCH_URL.format(page=1), params)
    return [parse(r) for r in (data or {}).get("results", [])]


def parse(r: dict) -> NormalizedJob:
    location = (r.get("location") or {}).get("display_name", "")
    posted = parse_iso(r.get("created"))
    return NormalizedJob(
        source="adzuna",
        external_id=str(r["id"]),
        title=(r.get("title") or "").strip(),
        company=(r.get("company") or {}).get("display_name", ""),
        location=location,
        remote=looks_remote(location, r.get("title", "")),
        salary=format_lpa(r.get("salary_min"), r.get("salary_max"),
                          estimated=str(r.get("salary_is_predicted")) == "1"),
        # Adzuna only returns a snippet; the full text lives on redirect_url.
        description=(r.get("description") or "").strip(),
        url=r.get("redirect_url", ""),
        posted_at=posted,
        posted_at_source="adzuna" if posted else "",
    )
