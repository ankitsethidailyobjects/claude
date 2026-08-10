"""
config.py — Paths, credentials, and run parameters for the Reddit audit system.

Reddit API credentials are read from the environment ONLY (never hard-coded and
never committed). Create a Reddit "script" app at
https://www.reddit.com/prefs/apps and export:

    export REDDIT_CLIENT_ID=...
    export REDDIT_CLIENT_SECRET=...
    export REDDIT_USER_AGENT="dailyobjects-audit by u/<yourname>"
    export REDDIT_USERNAME=...      # optional but recommended (raises rate limits)
    export REDDIT_PASSWORD=...      # optional

If no credentials are present the collector falls back to Reddit's public
unauthenticated JSON endpoints, which are heavily rate-limited and shallow —
fine for a smoke test, not for a full historical crawl.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---- Paths ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_MENTIONS_JSONL = DATA_DIR / "raw_mentions.jsonl"        # append-only raw crawl log
MASTER_CSV = DATA_DIR / "DailyObjects_Reddit_Master.csv"
MASTER_XLSX = DATA_DIR / "DailyObjects_Reddit_Master.xlsx"
SEEN_IDS_FILE = DATA_DIR / "seen_ids.txt"                   # dedup ledger for monthly reruns

DATA_DIR.mkdir(exist_ok=True)

# ---- Reddit credentials --------------------------------------------------
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "dailyobjects-reddit-audit/1.0")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

HAS_API_CREDS = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

# ---- Crawl parameters ----------------------------------------------------
# How many results to request per (query, sort) combination. Reddit caps search
# at ~250-1000 depending on endpoint; we page as far as it allows.
SEARCH_LIMIT_PER_QUERY = 250
SORTS = ["relevance", "new", "top", "comments"]
TIME_FILTERS = ["all"]              # 'all' for lifetime; add 'year','month' for reruns

# Rolling-window scope. When set (e.g. via `run.py --since-days 30`), the
# collector drops anything older than this many days and biases Reddit's own
# time filter toward the matching window ('month' for <=31d, 'year' for <=366d).
# None = lifetime crawl. This is what makes "last 30 days" a first-class mode.
SINCE_DAYS: int | None = None


def reddit_time_filter() -> str:
    """Map SINCE_DAYS to Reddit's coarse search time filter."""
    if SINCE_DAYS is None:
        return "all"
    if SINCE_DAYS <= 31:
        return "month"
    if SINCE_DAYS <= 93:
        return "month"
    if SINCE_DAYS <= 366:
        return "year"
    return "all"
FETCH_COMMENTS = True               # expand comment trees on matched posts (Agent 2)
MAX_COMMENTS_PER_POST = 500
POLITE_SLEEP_SECONDS = 1.0          # between API calls when unauthenticated

# Minimum body length (chars) for a comment to count as a "meaningful observation".
MIN_COMMENT_CHARS = 15
