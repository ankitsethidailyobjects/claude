"""One job shape for every source, plus the text/date/location helpers sources share."""

import hashlib
import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Optional


@dataclass
class NormalizedJob:
    source: str  # e.g. "greenhouse:groww", "google_jobs", "adzuna", "manual"
    external_id: str
    title: str
    company: str
    location: str = ""
    remote: bool = False
    experience: str = ""
    salary: str = ""
    description: str = ""
    url: str = ""
    posted_at: Optional[datetime] = None
    posted_at_source: str = ""


# Alternate spellings → one canonical city, so "Gurgaon" and "Gurugram" dedupe and match.
CITY_ALIASES = {
    "bengaluru": ["bengaluru", "bangalore"],
    "gurugram": ["gurugram", "gurgaon"],
    "mumbai": ["mumbai", "bombay", "navi mumbai", "thane"],
    "delhi": ["delhi", "new delhi"],
    "noida": ["noida", "greater noida"],
    "chennai": ["chennai", "madras"],
    "kolkata": ["kolkata", "calcutta"],
    "pune": ["pune"],
    "hyderabad": ["hyderabad", "secunderabad"],
    "ahmedabad": ["ahmedabad"],
    "jaipur": ["jaipur"],
    "chandigarh": ["chandigarh", "mohali", "panchkula"],
    "kochi": ["kochi", "cochin"],
}
_ALIAS_TO_CITY = {alias: city for city, aliases in CITY_ALIASES.items() for alias in aliases}
NCR = {"delhi", "gurugram", "noida", "faridabad", "ghaziabad"}

_REMOTE_RE = re.compile(r"\b(remote|work from home|wfh)\b", re.I)


def canonical_cities(text: str) -> set[str]:
    """All known cities mentioned in a location string ("Delhi NCR" counts as every NCR city)."""
    low = (text or "").lower()
    found = {city for alias, city in _ALIAS_TO_CITY.items() if re.search(rf"\b{re.escape(alias)}\b", low)}
    if re.search(r"\bncr\b", low):
        found |= NCR
    return found


def looks_remote(*texts: str) -> bool:
    return any(_REMOTE_RE.search(t or "") for t in texts)


class _TextExtractor(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "tr", "section"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("• ")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    raw = html.unescape(raw)  # Greenhouse double-escapes its HTML
    parser = _TextExtractor()
    parser.feed(raw)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


_LEGAL_SUFFIX = re.compile(
    r"\b(private limited|pvt\.? ltd\.?|pvt|limited|ltd\.?|inc\.?|llp|llc|corp\.?|co\.)$", re.I
)


def normalize_company(name: str) -> str:
    name = re.sub(r"[^\w\s.&]", " ", (name or "").lower()).strip()
    for _ in range(2):
        name = _LEGAL_SUFFIX.sub("", name).strip(" .,")
    return re.sub(r"\s+", " ", name)


def dedupe_hash(company: str, title: str, location: str) -> str:
    title_key = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()
    cities = sorted(canonical_cities(location))
    loc_key = cities[0] if cities else re.sub(r"[^a-z]+", " ", (location or "").lower()).strip()
    key = f"{normalize_company(company)}|{title_key}|{loc_key}"
    return hashlib.sha256(key.encode()).hexdigest()[:20]


_RELATIVE_RE = re.compile(r"(\d+|an?|one)\+?\s*(minute|min|hour|hr|day|week|month)s?\s+ago", re.I)


def parse_relative_date(text: str, now: datetime) -> Optional[datetime]:
    """'3 days ago', '30+ days ago', 'an hour ago', 'Just posted', 'Today' → datetime."""
    if not text:
        return None
    low = text.lower().strip()
    if low in {"just posted", "today", "just now", "few hours ago"} or "just" in low:
        return now
    if low == "yesterday":
        return now - timedelta(days=1)
    m = _RELATIVE_RE.search(low)
    if not m:
        return None
    count = 1 if m.group(1) in {"a", "an", "one"} else int(m.group(1))
    unit = m.group(2)
    delta = {
        "minute": timedelta(minutes=count),
        "min": timedelta(minutes=count),
        "hour": timedelta(hours=count),
        "hr": timedelta(hours=count),
        "day": timedelta(days=count),
        "week": timedelta(weeks=count),
        "month": timedelta(days=30 * count),
    }[unit]
    return now - delta


def parse_iso(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def from_epoch_ms(value) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def format_lpa(min_inr: float | None, max_inr: float | None, estimated: bool = False) -> str:
    """Annual INR → '₹12–18 LPA'."""
    vals = [v for v in (min_inr, max_inr) if v]
    if not vals:
        return ""
    lo, hi = min(vals) / 1e5, max(vals) / 1e5
    text = f"₹{lo:.0f} LPA" if round(lo) == round(hi) else f"₹{lo:.0f}–{hi:.0f} LPA"
    return text + (" (est.)" if estimated else "")
