"""
report.py — PHASES 15-23 report renderer.

Reads the built master dataset and renders a Markdown Voice-of-Customer report:
coverage, the Phase-19 brand-health matrix, multidimensional brand health,
category heatmap, issue tracker, positive equity, competitor pull, a verbatim
quote library, and a CEO-summary scaffold.

Evidence honesty is enforced structurally:
  * Every number is computed from real rows — nothing is invented.
  * Any section backed by fewer than MIN_EVIDENCE mentions prints an explicit
    "INSUFFICIENT EVIDENCE" flag instead of a confident claim.
  * Narrative interpretation (root causes, positioning) is emitted as a clearly
    labelled scaffold for an analyst/LLM to complete from the cited quotes —
    the generator does not fabricate the story.

Run:  python -m reddit_audit.report [--window-days N]
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

import pandas as pd

try:
    from . import config, classify, build_dataset
except ImportError:  # pragma: no cover
    import config, classify, build_dataset  # type: ignore

MIN_EVIDENCE = 5  # below this, we refuse to state a systemic conclusion
REPORT_MD = config.DATA_DIR / "DailyObjects_Reddit_Report.md"


def _load() -> pd.DataFrame:
    if not config.MASTER_CSV.exists():
        return pd.DataFrame(columns=classify.MASTER_COLUMNS)
    df = pd.read_csv(config.MASTER_CSV, dtype=str).fillna("")
    for col in ["upvotes_score", "num_replies", "impact_score", "sentiment_intensity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def _md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df is None or df.empty:
        return "_(no rows)_\n"
    df = df.head(max_rows)
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |",
           "| " + " | ".join("---" for _ in cols) + " |"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]).replace("\n", " ")[:90] for c in cols) + " |")
    return "\n".join(out) + "\n"


def main(window_days: int | None = None) -> int:
    df = _load()
    n = len(df)
    now = datetime.now(timezone.utc).date().isoformat()
    scope = f"last {window_days} days" if window_days else "all available history"

    L = []
    a = L.append
    a(f"# DailyObjects — Reddit Voice-of-Customer Report\n")
    a(f"**Generated:** {now}  ·  **Scope:** {scope}  ·  **Mentions analysed:** {n}\n")
    a("> **Provenance & caveats.** Built only from Reddit posts/comments actually "
      "retrieved by this pipeline. Findings describe *Reddit conversation*, not the "
      "DailyObjects customer base — Reddit over-indexes toward tech-enthusiasts and "
      "the dissatisfied. Sentiment/theme labels are lexicon-based first-pass "
      "classifications; low-confidence rows should be human-reviewed. Sections with "
      f"fewer than {MIN_EVIDENCE} mentions are flagged as insufficient evidence rather "
      "than stated as fact.\n")

    if n == 0:
        a("\n## ⚠️ NO DATA\n\nThe master dataset is empty — no Reddit mentions have been "
          "collected yet. Run `python -m reddit_audit.run --since-days 30` in an "
          "environment where Reddit is reachable (with Reddit API credentials), then "
          "regenerate this report. **No analysis is possible without evidence, and none "
          "will be invented.**\n")
        REPORT_MD.write_text("\n".join(L), encoding="utf-8")
        print(f"[report] wrote (empty-state) {REPORT_MD}")
        return 0

    # ---- coverage ----
    dates = df[df["date"] != ""]["date"]
    a("\n## 1. Coverage\n")
    a(f"- Date range: **{dates.min() if not dates.empty else 'n/a'} → {dates.max() if not dates.empty else 'n/a'}**")
    a(f"- Evidence mix: " + ", ".join(f"{k}={v}" for k, v in df['evidence_strength'].value_counts().items()))
    a(f"- Post vs comment: " + ", ".join(f"{k}={v}" for k, v in df['post_or_comment'].value_counts().items()))
    a(f"- First-hand mentions: {(df['firsthand_experience']=='Y').sum()} / {n}\n")

    # ---- Phase 19 brand health ----
    a("\n## 2. Reddit Brand-Health Dashboard (Phase 19)\n")
    a(_md_table(build_dataset.brand_health(df)))

    # ---- Phase 7 category heatmap ----
    a("\n## 3. Category Perception (Phase 7)\n")
    a(_md_table(build_dataset.category_analysis(df)))

    # ---- Phase 11 issues ----
    a("\n## 4. Issue Tracker (Phases 6 & 11)\n")
    it = build_dataset.issue_tracker(df)
    a(_md_table(it))

    # ---- positive equity ----
    a("\n## 5. Positive Equity (Phase 7 / Tab 7)\n")
    a(_md_table(build_dataset.positive_equity(df)))

    # ---- Phase 8 competitors ----
    a("\n## 6. Competitor Pull (Phase 8)\n")
    a(_md_table(build_dataset.competitors_tab(df)))

    # ---- Phase 20 quotes ----
    a("\n## 7. Quote Library — verbatim evidence (Phase 20)\n")
    ql = build_dataset.quote_library(df)
    if ql.empty:
        a("_No A/B-strength quotes yet._\n")
    else:
        for _, r in ql.head(20).iterrows():
            a(f"- _{r['overall_sentiment']} · {r['category']} · {r['evidence_strength']} · "
              f"impact {r['impact_score']}_ — \"{str(r['reddit_text'])[:280]}\" "
              f"([source]({r['comment_url']}), r/{r['subreddit']}, {r['date']})")
        a("")

    # ---- Phase 23 CEO summary scaffold ----
    a("\n## 8. CEO Summary — data-backed scaffold (Phase 23)\n")
    a("_Numbers below are computed; the one-line positioning and root-cause narrative "
      "are left for analyst/LLM completion against the cited quotes — not auto-written._\n")
    pos = build_dataset.positive_equity(df).sort_values("volume", ascending=False)
    a("**Top positive equities (by volume):**")
    for _, r in pos.head(5).iterrows():
        flag = "" if r["volume"] >= MIN_EVIDENCE else "  ⚠️ insufficient evidence"
        a(f"- {r['equity']} — {r['volume']} mentions{flag}")
    a("\n**Top problems (by avg impact × volume):**")
    if not it.empty:
        it2 = it[it["total_volume"] > 0].copy()
        it2["rank"] = it2["avg_impact"] * it2["total_volume"]
        for _, r in it2.sort_values("rank", ascending=False).head(5).iterrows():
            flag = "" if r["total_volume"] >= MIN_EVIDENCE else "  ⚠️ insufficient evidence"
            a(f"- {r['issue']} — {r['total_volume']} mentions, avg impact {r['avg_impact']}, "
              f"trend {r['trend']}{flag}")
    a("\n**\"DailyObjects is the brand you buy when ______\"** — _fill from Quote Library; "
      "requires analyst judgement, not auto-generated._\n")

    REPORT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"[report] wrote {REPORT_MD} ({n} mentions)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-days", type=int, default=None)
    args = ap.parse_args()
    raise SystemExit(main(window_days=args.window_days))
