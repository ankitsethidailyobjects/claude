"""Company careers boards: Greenhouse, Lever, Ashby (public APIs, no key)."""

from jobsearch.companies import BOARD_API
from jobsearch.http import get_json
from jobsearch.models import ATS, CompanyWatch
from jobsearch.normalize import NormalizedJob, from_epoch_ms, html_to_text, looks_remote, parse_iso


def source_name(company: CompanyWatch) -> str:
    return f"{company.ats.value}:{company.slug}"


def fetch_company(company: CompanyWatch) -> list[NormalizedJob]:
    data = get_json(BOARD_API[company.ats].format(slug=company.slug))
    if company.ats is ATS.greenhouse:
        return [parse_greenhouse(j, company) for j in (data or {}).get("jobs", [])]
    if company.ats is ATS.lever:
        return [parse_lever(j, company) for j in (data if isinstance(data, list) else [])]
    return [
        parse_ashby(j, company)
        for j in (data or {}).get("jobs", [])
        if j.get("isListed", True)
    ]


def parse_greenhouse(j: dict, company: CompanyWatch) -> NormalizedJob:
    location = (j.get("location") or {}).get("name", "")
    posted = parse_iso(j.get("first_published")) or parse_iso(j.get("updated_at"))
    return NormalizedJob(
        source=source_name(company),
        external_id=str(j["id"]),
        title=j.get("title", "").strip(),
        company=company.name,
        location=location,
        remote=looks_remote(location),
        description=html_to_text(j.get("content", "")),
        url=j.get("absolute_url", ""),
        posted_at=posted,
        posted_at_source="greenhouse" if posted else "",
    )


def parse_lever(j: dict, company: CompanyWatch) -> NormalizedJob:
    cats = j.get("categories") or {}
    location = cats.get("location") or ", ".join(cats.get("allLocations") or [])
    parts = [j.get("descriptionPlain") or html_to_text(j.get("description", ""))]
    for section in j.get("lists") or []:
        parts.append(section.get("text", ""))
        parts.append(html_to_text(section.get("content", "")))
    parts.append(j.get("additionalPlain", ""))
    posted = from_epoch_ms(j.get("createdAt"))
    return NormalizedJob(
        source=source_name(company),
        external_id=str(j["id"]),
        title=j.get("text", "").strip(),
        company=company.name,
        location=location,
        remote=j.get("workplaceType") == "remote" or looks_remote(location),
        description="\n\n".join(p for p in parts if p).strip(),
        url=j.get("hostedUrl", ""),
        posted_at=posted,
        posted_at_source="lever" if posted else "",
    )


def parse_ashby(j: dict, company: CompanyWatch) -> NormalizedJob:
    location = j.get("location", "")
    posted = parse_iso(j.get("publishedAt"))
    return NormalizedJob(
        source=source_name(company),
        external_id=str(j["id"]),
        title=j.get("title", "").strip(),
        company=company.name,
        location=location,
        remote=bool(j.get("isRemote")) or looks_remote(location),
        description=j.get("descriptionPlain") or html_to_text(j.get("descriptionHtml", "")),
        url=j.get("jobUrl", ""),
        posted_at=posted,
        posted_at_source="ashby" if posted else "",
    )
