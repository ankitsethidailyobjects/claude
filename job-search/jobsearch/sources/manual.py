"""Jobs pasted in by hand (LinkedIn, Naukri, referrals, anything)."""

import hashlib
from datetime import datetime

from jobsearch.normalize import NormalizedJob, looks_remote


def make_job(title: str, company: str, location: str = "", url: str = "", description: str = "",
             posted_at: datetime | None = None, salary: str = "") -> NormalizedJob:
    if not title.strip() or not company.strip():
        raise ValueError("Title and company are required")
    ext = url.strip() or hashlib.sha256(f"{title}|{company}|{location}".lower().encode()).hexdigest()[:20]
    return NormalizedJob(
        source="manual",
        external_id=ext,
        title=title.strip(),
        company=company.strip(),
        location=location.strip(),
        remote=looks_remote(location),
        salary=salary.strip(),
        description=description.strip(),
        url=url.strip(),
        posted_at=posted_at,
        posted_at_source="manual" if posted_at else "",
    )
