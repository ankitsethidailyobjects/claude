"""Cheap rule-based relevance check, run before any AI scoring.

Company boards return every opening (engineering, sales, ...), so this keeps only the
ones that fit the profile. It runs at display time, so editing the profile takes effect
immediately without re-fetching.
"""

import re

from jobsearch.models import Job, Profile
from jobsearch.normalize import canonical_cities

# Words that don't say what the job is about ("Senior Category Manager" is about "category").
GENERIC = {
    "manager", "senior", "sr", "lead", "head", "associate", "executive", "specialist",
    "assistant", "deputy", "junior", "jr", "principal", "of", "and", "the", "ii", "iii",
    "i", "iv", "director", "vp", "vice", "president", "chief", "officer", "team", "staff",
    "for", "in", "at", "&", "-", "general", "group", "key",
}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#]+", (text or "").lower())


def _stem(word: str) -> str:
    return word[:6] if len(word) > 6 else word


def title_matches(job_title: str, target: str) -> bool:
    core = [w for w in _words(target) if w not in GENERIC] or _words(target)
    stems = {_stem(w) for w in _words(job_title)}
    return bool(core) and all(_stem(w) in stems for w in core)


def matches_profile(job: Job, profile: Profile) -> tuple[bool, str]:
    if profile.target_titles and not any(title_matches(job.title, t) for t in profile.target_titles):
        return False, "title"
    haystack = f"{job.title}\n{job.description}".lower()
    for word in profile.deal_breakers:
        if re.search(rf"\b{re.escape(word.lower())}\b", haystack):
            return False, f"deal-breaker: {word}"
    if profile.cities and job.location and not job.remote:
        wanted = set().union(*(canonical_cities(c) or {c.lower()} for c in profile.cities))
        found = canonical_cities(job.location)
        if found and not (found & wanted):
            return False, "location"
        if not found and not any(c.lower() in job.location.lower() for c in profile.cities) \
                and "india" not in job.location.lower():
            return False, "location"
    if job.remote and not profile.remote_ok and profile.cities and not canonical_cities(job.location):
        return False, "remote"
    return True, ""
