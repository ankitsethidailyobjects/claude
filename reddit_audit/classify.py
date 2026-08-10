"""
classify.py — AGENT 3 (Evidence Quality) + theme, sentiment & impact scoring.

Turns each raw observation from collect.py into a fully-populated master row
(~45 fields from the brief's Master Dataset Structure). All labelling is
transparent and rule/lexicon based so monthly reruns are reproducible and every
label is auditable back to the cue that produced it (Principle #1).

Where confidence is low the row keeps its raw text intact and flags
`classification_confidence` = 'low' with a note, so a human/LLM reviewer can
override before the row influences a business decision. Nothing here fabricates
evidence — it only labels text that collect.py actually retrieved.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

try:
    from . import taxonomy
except ImportError:  # pragma: no cover
    import taxonomy  # type: ignore

_WORD = re.compile(r"[a-z0-9']+")


# --------------------------------------------------------------------------
# Sentiment  (Phase 6 — multidimensional)
# --------------------------------------------------------------------------
def _sentiment_score(text: str) -> tuple[float, int]:
    """Return (net_score, hits) using the weighted lexicon with negation + intensifiers."""
    low = f" {text.lower()} "
    tokens = _WORD.findall(low)
    score = 0.0
    hits = 0

    # phrase-level hits first (multi-word terms)
    for term, w in {**taxonomy.POSITIVE_TERMS, **taxonomy.NEGATIVE_TERMS}.items():
        if " " in term and term in low:
            score += w
            hits += 1

    # token-level with negation/intensifier lookback
    for i, tok in enumerate(tokens):
        w = taxonomy.POSITIVE_TERMS.get(tok) or taxonomy.NEGATIVE_TERMS.get(tok)
        if w is None:
            continue
        hits += 1
        mult = 1.0
        window = tokens[max(0, i - 3): i]
        if any(n in window for n in taxonomy.NEGATORS):
            mult *= -1.0
        for intens, im in taxonomy.INTENSIFIERS.items():
            if intens in window:
                mult *= im
        score += w * mult
    return score, hits


def _label_sentiment(score: float) -> str:
    if score >= 4:
        return "Positive"
    if score >= 1:
        return "Slightly Positive"
    if score <= -4:
        return "Strong Negative"
    if score <= -1:
        return "Negative"
    return "Neutral"


def _dimension_sentiment(text: str, theme_keywords: list[str]) -> str:
    """Sentiment of only the clauses that touch a given dimension's keywords."""
    low = text.lower()
    clauses = re.split(r"[.!?;\n]", low)
    relevant = [c for c in clauses if any(k in c for k in theme_keywords)]
    if not relevant:
        return "N/A"
    s, _ = _sentiment_score(" ".join(relevant))
    return _label_sentiment(s)


# --------------------------------------------------------------------------
# Theme classification  (Phase 3)
# --------------------------------------------------------------------------
def _themes(text: str) -> tuple[str, str]:
    low = text.lower()
    ranked = []
    for theme, meta in taxonomy.THEME_TAXONOMY.items():
        n = sum(1 for k in meta["keywords"] if k in low)
        if n:
            ranked.append((n, theme))
    ranked.sort(reverse=True)
    primary = ranked[0][1] if ranked else "Unclassified"
    secondary = ranked[1][1] if len(ranked) > 1 else ""
    return primary, secondary


def categorize(text: str) -> str:
    low = text.lower()
    for cat, kws in taxonomy.CATEGORY_KEYWORDS.items():
        if any(k in low for k in kws):
            return cat
    return "Unspecified"


def _competitors(text: str) -> list[str]:
    low = text.lower()
    found = []
    for name, aliases in taxonomy.COMPETITORS.items():
        if any(a in low for a in aliases):
            found.append(name)
    return found


# --------------------------------------------------------------------------
# Evidence strength  (Agent 3) + user type + journey stage
# --------------------------------------------------------------------------
def _evidence_strength(text: str) -> tuple[str, bool]:
    low = text.lower()
    firsthand = any(c in low for c in taxonomy.FIRSTHAND_CUES)
    specific = bool(re.search(r"\b(month|year|week|day|₹|rs\.?\s*\d|drop|used it|after)\b", low))
    if firsthand and specific:
        return "A", True
    if firsthand:
        return "A", True
    if any(c in low for c in taxonomy.RECOMMENDATION_CUES) or any(c in low for c in taxonomy.COMPARISON_CUES):
        return "B", False
    if any(c in low for c in taxonomy.HEARSAY_CUES):
        return "D", False
    return "C", False


def _user_type(text: str) -> str:
    low = text.lower()
    for utype in ["Repeat customer", "Former customer", "First-hand customer", "Prospective customer"]:
        if any(c in low for c in taxonomy.USER_TYPE_CUES[utype]):
            return utype
    return "Unknown"


def _journey_stage(text: str) -> str:
    low = text.lower()
    for stage, cues in taxonomy.JOURNEY_CUES.items():
        if any(c in low for c in cues):
            return stage
    return "Unclear"


def _recommendation_intent(text: str, sent_label: str) -> str:
    low = text.lower()
    if any(c in low for c in ["never buy", "avoid", "stay away", "don't buy", "dont buy", "wouldn't recommend"]):
        return "Discourages"
    if any(c in low for c in taxonomy.RECOMMENDATION_CUES):
        return "Recommends"
    if sent_label in ("Positive", "Slightly Positive"):
        return "Leans positive"
    if sent_label in ("Negative", "Strong Negative"):
        return "Leans negative"
    return "Neutral/None"


# --------------------------------------------------------------------------
# Impact score  (Phase 10) — transparent, bounded composite.
# --------------------------------------------------------------------------
def impact_score(row: dict) -> float:
    """
    Reputational-impact weight for a single mention, ~0-10. Deliberately simple
    and explainable (brief: 'do not manufacture statistical precision').
        base intensity  : |sentiment| capped
        engagement      : log-ish upvote + reply contribution
        evidence quality: A/B weighted far above C/D
        recency         : mentions in the last 12 months weighted up
    """
    import math

    intensity = min(abs(row.get("_sent_raw", 0.0)), 6) / 6 * 3          # 0-3
    up = max(row.get("upvotes_score", 0), 0)
    replies = max(row.get("num_replies", 0), 0)
    engagement = min(math.log10(up + 1) + math.log10(replies + 1), 3)    # 0-3
    ev = {"A": 2.5, "B": 1.8, "C": 0.8, "D": 0.4}.get(row.get("evidence_strength", "C"), 0.8)
    recency = 0.0
    try:
        dt = datetime.fromisoformat(row["date"]).replace(tzinfo=timezone.utc)
        months = (datetime.now(timezone.utc) - dt).days / 30.0
        recency = 1.5 if months <= 12 else (0.8 if months <= 24 else 0.3)
    except Exception:
        recency = 0.5
    return round(intensity + engagement + ev + recency, 2)


# --------------------------------------------------------------------------
# Main row builder
# --------------------------------------------------------------------------
def classify_observation(obs: dict, mention_seq: int) -> dict:
    text = obs.get("text", "") or ""
    title = obs.get("thread_title", "") or ""
    blob = f"{title}\n{text}"

    created = obs.get("created_utc", 0) or 0
    try:
        dt = datetime.fromtimestamp(float(created), tz=timezone.utc)
        date_iso = dt.date().isoformat()
        year, quarter, month = dt.year, f"{dt.year}Q{(dt.month - 1)//3 + 1}", f"{dt.year}-{dt.month:02d}"
    except Exception:
        date_iso, year, quarter, month = "", "", "", ""

    sent_raw, hits = _sentiment_score(blob)
    sent_label = _label_sentiment(sent_raw)
    primary, secondary = _themes(blob)
    category = categorize(blob)
    comps = _competitors(blob)
    ev_strength, firsthand = _evidence_strength(blob)
    user_type = _user_type(blob)

    prod_kw = (taxonomy.THEME_TAXONOMY["Product — Design & Aesthetics"]["keywords"]
               + taxonomy.THEME_TAXONOMY["Product — Material & Build"]["keywords"]
               + taxonomy.THEME_TAXONOMY["Product — Functionality & Innovation"]["keywords"])
    qual_kw = taxonomy.THEME_TAXONOMY["Product — Durability & Reliability"]["keywords"]
    val_kw = (taxonomy.THEME_TAXONOMY["Value — Price & Worth"]["keywords"]
              + taxonomy.THEME_TAXONOMY["Value — Discounts & Sales"]["keywords"])
    brand_kw = (taxonomy.THEME_TAXONOMY["Brand — Trust & Perception"]["keywords"]
                + taxonomy.THEME_TAXONOMY["Brand — Originality vs Copy"]["keywords"])
    cx_kw = (taxonomy.THEME_TAXONOMY["CX — Delivery & Packaging"]["keywords"]
             + taxonomy.THEME_TAXONOMY["CX — Returns, Refunds & Warranty"]["keywords"]
             + taxonomy.THEME_TAXONOMY["CX — Customer Support"]["keywords"])

    low = blob.lower()
    product_failure = any(k in low for k in
                          ["stopped working", "broke", "peeled", "cracked", "died", "fell apart",
                           "defective", "came off", "print came off", "wore off"])
    support_issue = any(k in low for k in
                        ["no response", "ignored", "customer care", "customer service", "rude",
                         "unresponsive", "no reply"]) and sent_raw < 0
    return_issue = any(k in low for k in ["return", "refund", "replacement", "exchange", "warranty"])
    pricing_issue = any(k in low for k in ["overpriced", "too expensive", "not worth", "rip off",
                                           "ripoff", "markup", "overcharg"])

    confidence = "high" if hits >= 3 or ev_strength == "A" else ("medium" if hits >= 1 else "low")
    notes = []
    if confidence == "low":
        notes.append("lexicon found few signals — review manually")
    if "daily objects" in low and "dailyobjects" not in low:
        notes.append("matched loose 'daily objects' form")

    sent_label_dim = {
        "product": _dimension_sentiment(blob, prod_kw),
        "quality": _dimension_sentiment(blob, qual_kw),
        "value": _dimension_sentiment(blob, val_kw),
        "brand": _dimension_sentiment(blob, brand_kw),
        "cx": _dimension_sentiment(blob, cx_kw),
    }

    row = {
        "mention_id": f"DO-{mention_seq:06d}",
        "thread_id": obs.get("thread_id", ""),
        "comment_id": obs.get("comment_id", ""),
        "date": date_iso, "year": year, "quarter": quarter, "month": month,
        "subreddit": obs.get("subreddit", ""),
        "thread_title": title,
        "thread_url": obs.get("thread_url", ""),
        "comment_url": obs.get("comment_url", ""),
        "post_or_comment": obs.get("kind", ""),
        "reddit_text": text,
        "upvotes_score": int(obs.get("score", 0) or 0),
        "num_replies": int(obs.get("num_replies", 0) or 0),
        "dailyobjects_mentioned": "Y",
        "product_mentioned": category if category != "Unspecified" else "",
        "category": category,
        "specific_sku": "",  # filled by human/LLM pass when a named SKU appears
        "competitor_mentioned": "; ".join(comps),
        "purchase_journey_stage": _journey_stage(blob),
        "user_type": user_type,
        "firsthand_experience": "Y" if firsthand else "N",
        "evidence_strength": ev_strength,
        "overall_sentiment": sent_label,
        "sentiment_intensity": round(abs(sent_raw), 2),
        "product_sentiment": sent_label_dim["product"],
        "quality_sentiment": sent_label_dim["quality"],
        "value_sentiment": sent_label_dim["value"],
        "brand_sentiment": sent_label_dim["brand"],
        "cx_sentiment": sent_label_dim["cx"],
        "recommendation_intent": _recommendation_intent(blob, sent_label),
        "primary_theme": primary,
        "secondary_theme": secondary,
        "specific_complaint": "",  # populated below
        "specific_praise": "",
        "product_failure": "Y" if product_failure else "N",
        "customer_support_issue": "Y" if support_issue else "N",
        "return_refund_issue": "Y" if return_issue else "N",
        "pricing_value_issue": "Y" if pricing_issue else "N",
        "competitor_recommendation": "Y" if (comps and _recommendation_intent(blob, sent_label) == "Discourages") else "N",
        "duplicate_flag": "N",
        "classification_confidence": confidence,
        "research_notes": "; ".join(notes),
        # internal helpers (dropped before CSV if you prefer; kept for auditability)
        "_sent_raw": round(sent_raw, 2),
        "author": obs.get("author", ""),
    }

    # short extracted complaint/praise snippets (kept verbatim from the text)
    if sent_raw < 0:
        row["specific_complaint"] = _first_clause_with(text, list(taxonomy.NEGATIVE_TERMS))
    if sent_raw > 0:
        row["specific_praise"] = _first_clause_with(text, list(taxonomy.POSITIVE_TERMS))

    row["impact_score"] = impact_score(row)
    return row


def _first_clause_with(text: str, terms: list[str]) -> str:
    for clause in re.split(r"[.!?;\n]", text):
        cl = clause.strip()
        if cl and any(t in cl.lower() for t in terms):
            return cl[:240]
    return ""


# Canonical column order for the master dataset (Phase 2 structure).
MASTER_COLUMNS = [
    "mention_id", "thread_id", "comment_id", "date", "year", "quarter", "month",
    "subreddit", "thread_title", "thread_url", "comment_url", "post_or_comment",
    "reddit_text", "upvotes_score", "num_replies", "dailyobjects_mentioned",
    "product_mentioned", "category", "specific_sku", "competitor_mentioned",
    "purchase_journey_stage", "user_type", "firsthand_experience", "evidence_strength",
    "overall_sentiment", "sentiment_intensity", "product_sentiment", "quality_sentiment",
    "value_sentiment", "brand_sentiment", "cx_sentiment", "recommendation_intent",
    "primary_theme", "secondary_theme", "specific_complaint", "specific_praise",
    "product_failure", "customer_support_issue", "return_refund_issue", "pricing_value_issue",
    "competitor_recommendation", "impact_score", "duplicate_flag",
    "classification_confidence", "research_notes", "author",
]
