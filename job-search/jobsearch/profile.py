"""Read and update the single user profile."""

import hashlib
import json
import re

from sqlmodel import Session, select

from jobsearch.models import Profile, utcnow


def split_list(raw: str) -> list[str]:
    """Split comma/newline separated input, trimming blanks and duplicates."""
    seen: dict[str, str] = {}
    for item in re.split(r"[,\n]", raw or ""):
        item = item.strip()
        if item and item.lower() not in seen:
            seen[item.lower()] = item
    return list(seen.values())


def get_profile(session: Session) -> Profile:
    profile = session.exec(select(Profile)).first()
    if profile is None:
        profile = Profile()
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


def compute_version(profile: Profile) -> str:
    """Changes whenever the resume or anything that affects scoring changes."""
    payload = {
        "resume": profile.resume_text,
        "titles": profile.target_titles,
        "seniority": profile.seniority,
        "years": profile.years_experience,
        "cities": profile.cities,
        "remote_ok": profile.remote_ok,
        "min_ctc": profile.min_ctc_lpa,
        "must": profile.must_have_keywords,
        "deal_breakers": profile.deal_breakers,
    }
    blob = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


PREFERENCE_FIELDS = {
    "full_name",
    "target_titles",
    "seniority",
    "years_experience",
    "cities",
    "remote_ok",
    "min_ctc_lpa",
    "must_have_keywords",
    "deal_breakers",
}


def update_profile(session: Session, **changes) -> Profile:
    unknown = set(changes) - PREFERENCE_FIELDS - {"resume_filename", "resume_text"}
    if unknown:
        raise ValueError(f"Unknown profile fields: {sorted(unknown)}")
    profile = get_profile(session)
    for key, value in changes.items():
        setattr(profile, key, value)
    profile.resume_version = compute_version(profile)
    profile.updated_at = utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def is_complete(profile: Profile) -> bool:
    return bool(profile.resume_text and profile.target_titles and (profile.cities or profile.remote_ok))
