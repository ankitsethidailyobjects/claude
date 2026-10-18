"""Google Jobs via SerpAPI (free key: serpapi.com). Google indexes Naukri, LinkedIn,
iimjobs and company sites, so this reaches those portals without scraping them."""

import hashlib
import re
from datetime import datetime

from jobsearch.http import get_json
from jobsearch.normalize import NormalizedJob, looks_remote, parse_relative_date

SEARCH_URL = "https://serpapi.com/search.json"


def search(api_key: str, query: str, now: datetime) -> list[NormalizedJob]:
    params = {"engine": "google_jobs", "q": query, "gl": "in", "hl": "en", "api_key": api_key}
    data = get_json(SEARCH_URL, params)
    if isinstance(data, dict) and data.get("error"):
        # SerpAPI reports "no results" as an error string.
        if "hasn't returned any results" in data["error"]:
            return []
        raise RuntimeError(data["error"])
    return [parse(r, now) for r in (data or {}).get("jobs_results", [])]


def parse(r: dict, now: datetime) -> NormalizedJob:
    ext = r.get("detected_extensions") or {}
    posted_text = ext.get("posted_at") or next(
        (e for e in r.get("extensions", []) if "ago" in e.lower()), ""
    )
    posted = parse_relative_date(posted_text, now)
    options = r.get("apply_options") or []
    url = options[0]["link"] if options else r.get("share_link", "")
    via = re.sub(r"^via\s+", "", r.get("via", ""), flags=re.I)
    description = r.get("description", "")
    for h in r.get("job_highlights") or []:
        items = "\n".join(f"• {i}" for i in h.get("items", []))
        description += f"\n\n{h.get('title', '')}\n{items}"
    job_id = r.get("job_id") or hashlib.sha256(
        f"{r.get('title')}|{r.get('company_name')}|{r.get('location')}".encode()
    ).hexdigest()[:20]
    location = r.get("location", "")
    return NormalizedJob(
        source="google_jobs",
        external_id=job_id[:200],
        title=(r.get("title") or "").strip(),
        company=r.get("company_name", ""),
        location=location,
        remote=bool(ext.get("work_from_home")) or looks_remote(location),
        salary=ext.get("salary", ""),
        description=description.strip(),
        url=url,
        posted_at=posted,
        posted_at_source=f"google_jobs ({posted_text}{', via ' + via if via else ''})" if posted else "",
    )


def build_queries(titles: list[str], cities: list[str], remote_ok: bool) -> list[str]:
    places = list(cities) + (["remote"] if remote_ok else [])
    if not places:
        places = ["India"]
    return [f"{t} {('in ' + p) if p != 'remote' else 'remote India'}" for t in titles for p in places]
