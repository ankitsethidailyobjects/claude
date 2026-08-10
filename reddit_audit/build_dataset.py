"""
build_dataset.py — PHASE 2 dataset build + all downstream analysis tabs.

Reads the raw observations (data/raw_mentions.jsonl), classifies each one
(classify.py), deduplicates, and writes:
    * DailyObjects_Reddit_Master.csv   — RAW_MENTIONS, one row per mention
    * DailyObjects_Reddit_Master.xlsx  — 8 analysis tabs

The Excel tabs (RAW_MENTIONS, THEME_TAXONOMY, MONTHLY_TRENDS, CATEGORY_ANALYSIS,
COMPETITORS, ISSUE_TRACKER, POSITIVE_EQUITY_TRACKER, QUOTE_LIBRARY) plus a
BRAND_HEALTH dashboard are computed from the classified rows with pandas — so
the moment real mentions exist, every table populates itself. With an empty
crawl the workbook still builds, with headers and definitions in place, ready
for the first monthly run.

Run:  python -m reddit_audit.build_dataset
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta

import pandas as pd

try:
    from . import config, taxonomy, classify
except ImportError:  # pragma: no cover
    import config, taxonomy, classify  # type: ignore


NEG_LABELS = {"Negative", "Strong Negative"}
POS_LABELS = {"Positive", "Slightly Positive"}


def load_and_classify() -> pd.DataFrame:
    if not config.RAW_MENTIONS_JSONL.exists():
        print("[build] no raw_mentions.jsonl yet — building empty scaffold.")
        return pd.DataFrame(columns=classify.MASTER_COLUMNS)

    rows, seq = [], 0
    seen_urls = set()
    with config.RAW_MENTIONS_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obs = json.loads(line)
            # dedup on comment_url (falls back to thread+comment id)
            key = obs.get("comment_url") or f"{obs.get('thread_id')}:{obs.get('comment_id')}"
            dup = key in seen_urls
            seen_urls.add(key)
            seq += 1
            row = classify.classify_observation(obs, seq)
            if dup:
                row["duplicate_flag"] = "Y"
            rows.append(row)

    df = pd.DataFrame(rows)
    # keep only the canonical columns in the CSV/RAW tab (drop internal _sent_raw)
    for c in classify.MASTER_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df


# --------------------------------------------------------------------------
# Analysis tables
# --------------------------------------------------------------------------
def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["month", "mentions", "positive", "neutral", "negative",
                                     "strong_negative", "recommends", "avg_impact"])
    d = df[df["month"] != ""].copy()
    g = d.groupby("month")
    out = pd.DataFrame({
        "mentions": g.size(),
        "positive": g["overall_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "neutral": g["overall_sentiment"].apply(lambda s: (s == "Neutral").sum()),
        "negative": g["overall_sentiment"].apply(lambda s: (s == "Negative").sum()),
        "strong_negative": g["overall_sentiment"].apply(lambda s: (s == "Strong Negative").sum()),
        "recommends": g["recommendation_intent"].apply(lambda s: (s == "Recommends").sum()),
        "product_love": g["product_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "value_pos": g["value_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "cx_neg": g["cx_sentiment"].apply(lambda s: s.isin(NEG_LABELS).sum()),
        "avg_impact": g["impact_score"].mean().round(2),
    }).reset_index()
    out["positive_pct"] = (out["positive"] / out["mentions"] * 100).round(1)
    out["negative_pct"] = ((out["negative"] + out["strong_negative"]) / out["mentions"] * 100).round(1)
    return out.sort_values("month")


def category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["category", "mentions", "avg_sentiment_score", "positive_pct",
                                     "quality_neg", "recommends", "classification"])
    g = df.groupby("category")
    out = pd.DataFrame({
        "mentions": g.size(),
        "avg_impact": g["impact_score"].mean().round(2),
        "positive": g["overall_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "negative": g["overall_sentiment"].apply(lambda s: s.isin(NEG_LABELS).sum()),
        "product_love": g["product_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "quality_neg": g["quality_sentiment"].apply(lambda s: s.isin(NEG_LABELS).sum()),
        "value_pos": g["value_sentiment"].apply(lambda s: s.isin(POS_LABELS).sum()),
        "recommends": g["recommendation_intent"].apply(lambda s: (s == "Recommends").sum()),
        "product_failures": g["product_failure"].apply(lambda s: (s == "Y").sum()),
    }).reset_index()
    out["positive_pct"] = (out["positive"] / out["mentions"] * 100).round(1)

    def classify_cat(r):
        if r["mentions"] < 3:
            return "Insufficient data"
        if r["positive_pct"] >= 55 and r["quality_neg"] <= r["mentions"] * 0.2:
            return "BRAND BUILDER"
        if r["negative"] > r["positive"] or r["quality_neg"] > r["mentions"] * 0.35:
            return "REPUTATION RISK"
        return "NEUTRAL"

    out["classification"] = out.apply(classify_cat, axis=1)
    return out.sort_values("mentions", ascending=False)


def competitors_tab(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["competitor", "mentions", "sent_when_mentioned",
                                     "do_discouraged", "example_url"])
    rows = []
    d = df[df["competitor_mentioned"] != ""]
    for _, r in d.iterrows():
        for comp in str(r["competitor_mentioned"]).split("; "):
            if comp:
                rows.append({"competitor": comp, "sentiment": r["overall_sentiment"],
                             "do_discouraged": r["competitor_recommendation"],
                             "category": r["category"], "url": r["comment_url"],
                             "impact": r["impact_score"], "text": r["reddit_text"][:200]})
    if not rows:
        return pd.DataFrame(columns=["competitor", "mentions", "do_discouraged", "example_url"])
    cdf = pd.DataFrame(rows)
    g = cdf.groupby("competitor")
    out = pd.DataFrame({
        "mentions": g.size(),
        "do_discouraged_count": g["do_discouraged"].apply(lambda s: (s == "Y").sum()),
        "avg_impact": g["impact"].mean().round(2),
        "example_url": g["url"].first(),
        "example_text": g["text"].first(),
    }).reset_index().sort_values("mentions", ascending=False)
    return out


def issue_tracker(df: pd.DataFrame) -> pd.DataFrame:
    """Phase 6/11 issue-level rollup for the negative/CX/quality themes."""
    cols = ["issue", "first_seen", "last_seen", "total_volume", "recent_12m_volume",
            "trend", "avg_impact", "severity", "example_urls"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    issue_flags = {
        "Product failure / durability": df["product_failure"] == "Y",
        "Customer support failure": df["customer_support_issue"] == "Y",
        "Return / refund / warranty friction": df["return_refund_issue"] == "Y",
        "Pricing / value objection": df["pricing_value_issue"] == "Y",
    }
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).date().isoformat()
    rows = []
    for issue, mask in issue_flags.items():
        sub = df[mask & (df["date"] != "")]
        if sub.empty:
            rows.append({"issue": issue, "first_seen": "", "last_seen": "", "total_volume": 0,
                         "recent_12m_volume": 0, "trend": "no evidence", "avg_impact": 0,
                         "severity": "—", "example_urls": ""})
            continue
        recent = sub[sub["date"] >= cutoff]
        older = sub[sub["date"] < cutoff]
        trend = ("EMERGING" if len(recent) > len(older) else
                 "DECLINING" if len(recent) < len(older) * 0.5 else "PERSISTENT")
        if len(sub) < 3:
            trend = "ONE-OFF / NOISE"
        sev = "High" if sub["impact_score"].mean() >= 6 else ("Medium" if sub["impact_score"].mean() >= 4 else "Low")
        rows.append({
            "issue": issue, "first_seen": sub["date"].min(), "last_seen": sub["date"].max(),
            "total_volume": len(sub), "recent_12m_volume": len(recent), "trend": trend,
            "avg_impact": round(sub["impact_score"].mean(), 2), "severity": sev,
            "example_urls": " | ".join(sub.sort_values("impact_score", ascending=False)["comment_url"].head(3)),
        })
    return pd.DataFrame(rows, columns=cols)


def positive_equity(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["equity", "volume", "recent_12m_volume", "trend", "avg_impact", "example_urls"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    equities = {
        "Design / aesthetics love": df["product_sentiment"].isin(POS_LABELS),
        "Recommends / advocacy": df["recommendation_intent"] == "Recommends",
        "Value-for-money endorsement": df["value_sentiment"].isin(POS_LABELS),
        "Brand trust": df["brand_sentiment"].isin(POS_LABELS),
    }
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).date().isoformat()
    rows = []
    for eq, mask in equities.items():
        sub = df[mask & (df["date"] != "")]
        recent = sub[sub["date"] >= cutoff] if not sub.empty else sub
        rows.append({
            "equity": eq, "volume": len(sub), "recent_12m_volume": len(recent),
            "trend": "building" if not sub.empty and len(recent) >= len(sub) / 2 else "flat/declining",
            "avg_impact": round(sub["impact_score"].mean(), 2) if not sub.empty else 0,
            "example_urls": " | ".join(sub.sort_values("impact_score", ascending=False)["comment_url"].head(3)) if not sub.empty else "",
        })
    return pd.DataFrame(rows, columns=cols)


def quote_library(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["date", "subreddit", "category", "primary_theme", "overall_sentiment",
            "evidence_strength", "impact_score", "reddit_text", "comment_url"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    # strongest evidence first, keep a balanced mix of positive & negative
    keep = df[df["evidence_strength"].isin(["A", "B"])].sort_values("impact_score", ascending=False)
    return keep[cols].head(200)


def theme_taxonomy_tab() -> pd.DataFrame:
    rows = []
    for theme, meta in taxonomy.THEME_TAXONOMY.items():
        rows.append({"primary_theme": theme, "definition": meta["definition"],
                     "sub_themes": ", ".join(meta["subthemes"]),
                     "trigger_keywords": ", ".join(meta["keywords"][:12])})
    return pd.DataFrame(rows)


def brand_health(df: pd.DataFrame) -> pd.DataFrame:
    """Phase 19 dashboard: metric x time-window matrix."""
    windows = {"Historical (all)": None, "Last 12M": 365, "Last 6M": 182, "Last 3M": 91}
    metrics = {
        "Mention Volume": lambda x: len(x),
        "Positive Sentiment %": lambda x: round(x["overall_sentiment"].isin(POS_LABELS).mean() * 100, 1) if len(x) else 0,
        "Negative Sentiment %": lambda x: round(x["overall_sentiment"].isin(NEG_LABELS).mean() * 100, 1) if len(x) else 0,
        "Recommendation Intent %": lambda x: round((x["recommendation_intent"] == "Recommends").mean() * 100, 1) if len(x) else 0,
        "Product Love %": lambda x: round(x["product_sentiment"].isin(POS_LABELS).mean() * 100, 1) if len(x) else 0,
        "Quality Trust %": lambda x: round((1 - x["quality_sentiment"].isin(NEG_LABELS).mean()) * 100, 1) if len(x) else 0,
        "Value Perception %": lambda x: round(x["value_sentiment"].isin(POS_LABELS).mean() * 100, 1) if len(x) else 0,
        "CX Trust %": lambda x: round((1 - x["cx_sentiment"].isin(NEG_LABELS).mean()) * 100, 1) if len(x) else 0,
        "Brand Desirability %": lambda x: round(x["brand_sentiment"].isin(POS_LABELS).mean() * 100, 1) if len(x) else 0,
    }
    now = datetime.now(timezone.utc).date()
    result = {m: {} for m in metrics}
    for wname, days in windows.items():
        if df.empty:
            sub = df
        elif days is None:
            sub = df
        else:
            cutoff = (now - timedelta(days=days)).isoformat()
            sub = df[(df["date"] != "") & (df["date"] >= cutoff)]
        for m, fn in metrics.items():
            result[m][wname] = fn(sub)
    out = pd.DataFrame(result).T.reset_index().rename(columns={"index": "Metric"})
    return out


# --------------------------------------------------------------------------
# Workbook writer
# --------------------------------------------------------------------------
def write_workbook(df: pd.DataFrame) -> None:
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    raw = df[classify.MASTER_COLUMNS] if not df.empty else pd.DataFrame(columns=classify.MASTER_COLUMNS)

    tabs = {
        "RAW_MENTIONS": raw,
        "THEME_TAXONOMY": theme_taxonomy_tab(),
        "MONTHLY_TRENDS": monthly_trends(df),
        "CATEGORY_ANALYSIS": category_analysis(df),
        "COMPETITORS": competitors_tab(df),
        "ISSUE_TRACKER": issue_tracker(df),
        "POSITIVE_EQUITY_TRACKER": positive_equity(df),
        "QUOTE_LIBRARY": quote_library(df),
        "BRAND_HEALTH": brand_health(df),
    }

    with pd.ExcelWriter(config.MASTER_XLSX, engine="openpyxl") as xw:
        for name, tab in tabs.items():
            tab.to_excel(xw, sheet_name=name, index=False)

        wb = xw.book
        header_fill = PatternFill("solid", fgColor="1F2937")
        header_font = Font(color="FFFFFF", bold=True, size=10)
        for name in tabs:
            ws = wb[name]
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(vertical="center", wrap_text=True)
            ws.freeze_panes = "A2"
            # reasonable column widths
            for col in ws.columns:
                letter = get_column_letter(col[0].column)
                longest = max((len(str(c.value)) for c in col[:50] if c.value is not None), default=10)
                ws.column_dimensions[letter].width = min(max(longest + 2, 12), 60)

    print(f"[build] wrote workbook -> {config.MASTER_XLSX}")


def main() -> int:
    df = load_and_classify()
    # CSV (RAW_MENTIONS)
    (df[classify.MASTER_COLUMNS] if not df.empty
     else pd.DataFrame(columns=classify.MASTER_COLUMNS)).to_csv(config.MASTER_CSV, index=False)
    print(f"[build] wrote {len(df)} rows -> {config.MASTER_CSV}")
    write_workbook(df)

    if df.empty:
        print("[build] NOTE: dataset is empty. Run collect.py with Reddit access first; "
              "then rerun build_dataset to populate every analysis tab.")
    else:
        print(f"[build] categories seen: {df['category'].nunique()} | "
              f"date range: {df['date'].replace('', pd.NA).min()} -> {df['date'].replace('', pd.NA).max()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
