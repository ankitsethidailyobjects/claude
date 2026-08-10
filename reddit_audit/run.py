"""
run.py — Orchestrator for the multi-agent DailyObjects Reddit audit.

Chains the pipeline end to end:

    Agent 1 + 2  (collect.py)      Discovery + Extraction   -> data/raw_mentions.jsonl
    Agent 3      (classify.py)     Evidence quality + themes -> in-memory rows
    Phase 2      (build_dataset)   Master CSV + 8-tab XLSX   -> data/DailyObjects_Reddit_Master.*

Usage:
    python -m reddit_audit.run              # full run (collect + build)
    python -m reddit_audit.run --build-only # skip crawl, rebuild tabs from existing raw log
    python -m reddit_audit.run --check      # print environment/access readiness

The Strategic Synthesis (Phases 17-23) is intentionally NOT automated: it must be
written by an analyst/LLM reading the populated workbook, because it turns
evidence into judgement. build_dataset.py produces every input it needs.
"""

from __future__ import annotations

import argparse
import sys

try:
    from . import config, collect, build_dataset
except ImportError:  # pragma: no cover
    import config, collect, build_dataset  # type: ignore


def check() -> int:
    print("=== DailyObjects Reddit audit — readiness check ===")
    print(f"Reddit API credentials present : {config.HAS_API_CREDS}")
    print(f"  backend                      : {'PRAW (authenticated)' if config.HAS_API_CREDS else 'public JSON fallback'}")
    print(f"data dir                       : {config.DATA_DIR}")
    print(f"raw log exists                 : {config.RAW_MENTIONS_JSONL.exists()}")
    print(f"seen-ids ledger                : {len(collect.load_seen())} ids")
    # connectivity probe
    try:
        import requests
        r = requests.get("https://www.reddit.com/r/india/about.json",
                         headers={"User-Agent": config.REDDIT_USER_AGENT}, timeout=15)
        print(f"reddit.com reachable           : yes (HTTP {r.status_code})")
    except Exception as e:
        print(f"reddit.com reachable           : NO ({type(e).__name__}: {e})")
        print("  -> If this is a network-policy block, run in an environment that allows reddit.com.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the DailyObjects Reddit audit pipeline.")
    ap.add_argument("--build-only", action="store_true", help="skip crawl; rebuild tabs from raw log")
    ap.add_argument("--check", action="store_true", help="print readiness check and exit")
    args = ap.parse_args()

    if args.check:
        return check()

    if not args.build_only:
        print(">>> AGENT 1+2: discovery & extraction")
        collect.main()

    print(">>> AGENT 3 + PHASE 2: classification & dataset build")
    build_dataset.main()
    print(">>> done. Open data/DailyObjects_Reddit_Master.xlsx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
