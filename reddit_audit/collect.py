"""
collect.py — AGENT 1 (Discovery) + AGENT 2 (Evidence Extraction).

Discovers DailyObjects conversations across Reddit posts AND comments by fanning
out the Phase-1 search surface over multiple sort orders and (optionally) seed
subreddits, then extracts every meaningful mention as a raw observation WITHOUT
summarising away the original text (brief Principle #2 and Agent-2 rule).

Two backends:
  * PRAW (authenticated)  — used when REDDIT_CLIENT_ID/SECRET are set. Robust,
    higher rate limits, comment-tree expansion.
  * Public JSON (fallback)— unauthenticated requests to *.reddit.com/*.json.
    Shallow + rate-limited; use only for a smoke test.

Output: append-only JSONL at data/raw_mentions.jsonl, one object per post or
comment, with a stable dedup ledger (data/seen_ids.txt) so monthly reruns only
add genuinely new material (Phase 24, steps 1-3).

Run:  python -m reddit_audit.collect            # from repo root
  or  python reddit_audit/collect.py
"""

from __future__ import annotations

import json
import time
import sys
from datetime import datetime, timezone
from typing import Iterable

try:  # allow both `python -m reddit_audit.collect` and direct execution
    from . import config, taxonomy
except ImportError:  # pragma: no cover
    import config, taxonomy  # type: ignore


# --------------------------------------------------------------------------
# Dedup ledger
# --------------------------------------------------------------------------
def load_seen() -> set[str]:
    if config.SEEN_IDS_FILE.exists():
        return set(config.SEEN_IDS_FILE.read_text().split())
    return set()


def append_seen(ids: Iterable[str]) -> None:
    with config.SEEN_IDS_FILE.open("a") as fh:
        for i in ids:
            fh.write(i + "\n")


def _cutoff_ts() -> float:
    """Epoch seconds before which mentions are dropped (0 = no window)."""
    if config.SINCE_DAYS is None:
        return 0.0
    return time.time() - config.SINCE_DAYS * 86400


def _too_old(created_utc: float, cutoff: float) -> bool:
    return cutoff > 0 and float(created_utc or 0) < cutoff


def _matches_brand(text: str) -> bool:
    """True if text plausibly refers to DailyObjects (not just 'daily objects' noise)."""
    low = (text or "").lower()
    if "dailyobjects" in low or "dailyobjects.com" in low:
        return True
    if "daily objects" in low:
        # loose form: require a product/brand context token nearby to cut noise
        context = ["case", "cover", "bag", "sleeve", "charger", "cable", "strap",
                   "wallet", "backpack", "order", "brand", "bought", "quality", "phone"]
        return any(c in low for c in context)
    return False


def _record(kind: str, obj: dict) -> dict:
    """Normalise a PRAW/JSON item into the raw-observation schema."""
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "kind": kind,  # 'post' | 'comment'
        **obj,
    }


# --------------------------------------------------------------------------
# PRAW backend
# --------------------------------------------------------------------------
def collect_with_praw(out, seen: set[str]) -> list[str]:
    import praw

    kwargs = dict(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )
    if config.REDDIT_USERNAME and config.REDDIT_PASSWORD:
        kwargs.update(username=config.REDDIT_USERNAME, password=config.REDDIT_PASSWORD)
    reddit = praw.Reddit(**kwargs)
    reddit.read_only = True

    new_ids: list[str] = []
    cutoff = _cutoff_ts()

    def emit(rec: dict, uid: str):
        if uid in seen:
            return
        seen.add(uid)
        new_ids.append(uid)
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    tf = config.reddit_time_filter()
    # ---- site-wide + seed-subreddit search over the full query surface ----
    targets = ["all"] + taxonomy.SEED_SUBREDDITS
    for sub in targets:
        for query in taxonomy.SEARCH_QUERIES:
            for sort in config.SORTS:
                try:
                    listing = reddit.subreddit(sub).search(
                        query, sort=sort, time_filter=tf,
                        limit=config.SEARCH_LIMIT_PER_QUERY,
                    )
                    for post in listing:
                        _handle_post(post, emit, config, cutoff)
                except Exception as e:  # network / 429 / private sub — log & continue
                    print(f"  ! search failed sub={sub} q='{query}' sort={sort}: {e}", file=sys.stderr)
                    time.sleep(2)
    return new_ids


def _handle_post(post, emit, config, cutoff: float = 0.0) -> None:
    title = getattr(post, "title", "") or ""
    body = getattr(post, "selftext", "") or ""
    post_uid = f"t3_{post.id}"
    blob = f"{title}\n{body}"

    if _matches_brand(blob) and not _too_old(getattr(post, "created_utc", 0), cutoff):
        emit(_record("post", {
            "thread_id": post.id, "comment_id": "",
            "subreddit": str(post.subreddit), "thread_title": title,
            "thread_url": f"https://www.reddit.com{post.permalink}",
            "comment_url": f"https://www.reddit.com{post.permalink}",
            "text": body if body else title,
            "score": int(getattr(post, "score", 0)),
            "num_replies": int(getattr(post, "num_comments", 0)),
            "created_utc": float(getattr(post, "created_utc", 0)),
            "author": str(getattr(post, "author", "") or "[deleted]"),
        }), post_uid)

    # Expand comments on ANY matched thread OR any thread whose title matched,
    # because DailyObjects is frequently mentioned only inside comments.
    if config.FETCH_COMMENTS:
        try:
            post.comments.replace_more(limit=0)
            for c in post.comments.list()[: config.MAX_COMMENTS_PER_POST]:
                cbody = getattr(c, "body", "") or ""
                if len(cbody) < config.MIN_COMMENT_CHARS:
                    continue
                if not _matches_brand(cbody):
                    continue
                if _too_old(getattr(c, "created_utc", 0), cutoff):
                    continue
                emit(_record("comment", {
                    "thread_id": post.id, "comment_id": c.id,
                    "subreddit": str(post.subreddit), "thread_title": title,
                    "thread_url": f"https://www.reddit.com{post.permalink}",
                    "comment_url": f"https://www.reddit.com{post.permalink}{c.id}/",
                    "text": cbody,
                    "score": int(getattr(c, "score", 0)),
                    "num_replies": len(getattr(c, "replies", []) or []),
                    "created_utc": float(getattr(c, "created_utc", 0)),
                    "author": str(getattr(c, "author", "") or "[deleted]"),
                }), f"t1_{c.id}")
        except Exception as e:
            print(f"  ! comment expand failed on {post.id}: {e}", file=sys.stderr)


# --------------------------------------------------------------------------
# Public-JSON fallback backend
# --------------------------------------------------------------------------
def collect_with_public_json(out, seen: set[str]) -> list[str]:
    import requests

    headers = {"User-Agent": config.REDDIT_USER_AGENT}
    new_ids: list[str] = []
    cutoff = _cutoff_ts()
    sess = requests.Session()

    for query in taxonomy.SEARCH_QUERIES:
        for sort in config.SORTS:
            url = "https://www.reddit.com/search.json"
            params = {"q": query, "sort": sort, "limit": 100,
                      "t": config.reddit_time_filter(), "raw_json": 1}
            try:
                r = sess.get(url, params=params, headers=headers, timeout=30)
                if r.status_code != 200:
                    print(f"  ! HTTP {r.status_code} q='{query}' sort={sort}", file=sys.stderr)
                    time.sleep(config.POLITE_SLEEP_SECONDS)
                    continue
                children = r.json().get("data", {}).get("children", [])
                for ch in children:
                    d = ch.get("data", {})
                    title = d.get("title", "") or ""
                    body = d.get("selftext", "") or ""
                    if not _matches_brand(f"{title}\n{body}"):
                        continue
                    if _too_old(d.get("created_utc", 0), cutoff):
                        continue
                    uid = "t3_" + d.get("id", "")
                    if uid in seen:
                        continue
                    seen.add(uid); new_ids.append(uid)
                    out.write(json.dumps(_record("post", {
                        "thread_id": d.get("id", ""), "comment_id": "",
                        "subreddit": d.get("subreddit", ""), "thread_title": title,
                        "thread_url": "https://www.reddit.com" + d.get("permalink", ""),
                        "comment_url": "https://www.reddit.com" + d.get("permalink", ""),
                        "text": body if body else title,
                        "score": int(d.get("score", 0)),
                        "num_replies": int(d.get("num_comments", 0)),
                        "created_utc": float(d.get("created_utc", 0)),
                        "author": d.get("author", ""),
                    }), ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"  ! request failed q='{query}': {e}", file=sys.stderr)
            time.sleep(config.POLITE_SLEEP_SECONDS)
    return new_ids


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def main() -> int:
    seen = load_seen()
    print(f"[collect] dedup ledger holds {len(seen)} known ids")
    print(f"[collect] backend = {'PRAW (authenticated)' if config.HAS_API_CREDS else 'public JSON (fallback)'}")

    with config.RAW_MENTIONS_JSONL.open("a", encoding="utf-8") as out:
        if config.HAS_API_CREDS:
            new_ids = collect_with_praw(out, seen)
        else:
            new_ids = collect_with_public_json(out, seen)

    append_seen(new_ids)
    print(f"[collect] added {len(new_ids)} new raw observations -> {config.RAW_MENTIONS_JSONL}")
    if not new_ids and not config.HAS_API_CREDS:
        print("[collect] NOTE: 0 rows via public JSON usually means Reddit is blocked or "
              "rate-limiting. Set API credentials and/or ensure network egress allows reddit.com.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
