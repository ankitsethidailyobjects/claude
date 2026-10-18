from datetime import datetime, timedelta, timezone

from jobsearch.normalize import (
    canonical_cities,
    dedupe_hash,
    format_lpa,
    html_to_text,
    normalize_company,
    parse_relative_date,
)

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def test_relative_dates():
    assert parse_relative_date("3 days ago", NOW) == NOW - timedelta(days=3)
    assert parse_relative_date("30+ days ago", NOW) == NOW - timedelta(days=30)
    assert parse_relative_date("an hour ago", NOW) == NOW - timedelta(hours=1)
    assert parse_relative_date("Just posted", NOW) == NOW
    assert parse_relative_date("2 weeks ago", NOW) == NOW - timedelta(weeks=2)
    assert parse_relative_date("Full-time", NOW) is None


def test_city_aliases():
    assert canonical_cities("Gurgaon, Haryana, India") == {"gurugram"}
    assert canonical_cities("Bangalore / Mumbai") == {"bengaluru", "mumbai"}
    assert "noida" in canonical_cities("Delhi NCR")


def test_dedupe_hash_ignores_legal_suffix_case_and_city_alias():
    a = dedupe_hash("DailyObjects Pvt. Ltd.", "Category Manager", "Gurgaon, Haryana")
    b = dedupe_hash("dailyobjects", "category manager ", "Gurugram")
    assert a == b
    assert a != dedupe_hash("dailyobjects", "category manager", "Mumbai")


def test_normalize_company():
    assert normalize_company("Razorpay Software Private Limited") == "razorpay software"


def test_html_to_text_unescapes_greenhouse():
    text = html_to_text("&lt;p&gt;Hello&lt;/p&gt;&lt;ul&gt;&lt;li&gt;SQL&lt;/li&gt;&lt;/ul&gt;")
    assert "Hello" in text and "• SQL" in text and "<" not in text


def test_format_lpa():
    assert format_lpa(1200000, 1800000) == "₹12–18 LPA"
    assert format_lpa(1500000, 1500000, estimated=True) == "₹15 LPA (est.)"
    assert format_lpa(None, None) == ""
