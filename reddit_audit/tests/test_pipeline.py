"""
Smoke tests for the classification + dataset build.

The strings below are HAND-WRITTEN FIXTURES invented to exercise the classifier.
They are NOT real Reddit data and are never written to the master dataset — they
only assert that classify.py assigns sane labels. Run: python -m pytest, or
just `python reddit_audit/tests/test_pipeline.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify  # noqa: E402
import build_dataset  # noqa: E402
import pandas as pd  # noqa: E402


FIXTURES = [
    {  # strong first-hand positive, phone case
        "kind": "comment", "thread_title": "Best phone cases in India?",
        "text": "I bought a DailyObjects leather case for my iPhone 14 and have been using it "
                "for 8 months. Absolutely love it, the material quality is premium and it has "
                "held up great. Worth every rupee, highly recommend.",
        "subreddit": "india", "score": 42, "num_replies": 5,
        "created_utc": 1700000000, "thread_id": "aaa", "comment_id": "c1",
        "thread_url": "https://www.reddit.com/x", "comment_url": "https://www.reddit.com/x/c1/",
    },
    {  # negative durability + support, competitor
        "kind": "comment", "thread_title": "DailyObjects vs Spigen",
        "text": "Avoid DailyObjects. My case peeled and the print came off within 2 months. "
                "Customer service ignored my warranty claim. Overpriced for what it is, "
                "just get Spigen instead.",
        "subreddit": "apple", "score": 88, "num_replies": 20,
        "created_utc": 1720000000, "thread_id": "bbb", "comment_id": "c2",
        "thread_url": "https://www.reddit.com/y", "comment_url": "https://www.reddit.com/y/c2/",
    },
    {  # hearsay, neutral
        "kind": "post", "thread_title": "Daily Objects bags any good?",
        "text": "Thinking of buying a DailyObjects backpack. Apparently people say they are "
                "decent but I've heard mixed things. Is it worth it?",
        "subreddit": "onebag", "score": 3, "num_replies": 1,
        "created_utc": 1730000000, "thread_id": "ccc", "comment_id": "",
        "thread_url": "https://www.reddit.com/z", "comment_url": "https://www.reddit.com/z",
    },
]


def test_classification_labels():
    r0 = classify.classify_observation(FIXTURES[0], 1)
    assert r0["category"] == "Phone Cases"
    assert r0["overall_sentiment"] in ("Positive", "Slightly Positive")
    assert r0["evidence_strength"] == "A"
    assert r0["firsthand_experience"] == "Y"
    assert r0["recommendation_intent"] == "Recommends"

    r1 = classify.classify_observation(FIXTURES[1], 2)
    assert r1["overall_sentiment"] in ("Negative", "Strong Negative")
    assert r1["product_failure"] == "Y"
    assert "Spigen" in r1["competitor_mentioned"]
    assert r1["recommendation_intent"] == "Discourages"

    r2 = classify.classify_observation(FIXTURES[2], 3)
    assert r2["category"] == "Backpacks"
    assert r2["evidence_strength"] == "D"  # hearsay
    assert r2["user_type"] == "Prospective customer"
    print("OK  classification labels")


def test_analysis_tables_build():
    rows = [classify.classify_observation(f, i + 1) for i, f in enumerate(FIXTURES)]
    df = pd.DataFrame(rows)
    for c in classify.MASTER_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    assert not build_dataset.monthly_trends(df).empty
    assert not build_dataset.category_analysis(df).empty
    assert not build_dataset.brand_health(df).empty
    it = build_dataset.issue_tracker(df)
    assert (it["issue"] == "Product failure / durability").any()
    print("OK  analysis tables build")


if __name__ == "__main__":
    test_classification_labels()
    test_analysis_tables_build()
    print("\nAll smoke tests passed.")
