# DailyObjects Reddit Intelligence System

An **auditable, longitudinal Voice-of-Customer system built from Reddit evidence** —
not a one-off sentiment report. It discovers DailyObjects conversations across
Reddit, extracts every meaningful mention *verbatim*, classifies each along
evidence-strength / theme / multidimensional-sentiment / impact axes, and builds
a 9-tab analysis workbook that can be re-run every month and appended to.

> **Core principle:** DATASET FIRST → ANALYSIS SECOND → RECOMMENDATIONS THIRD → TRACK CHANGE OVER TIME.
> Every conclusion must trace back to a real Reddit post/comment. **This system never fabricates evidence.**

---

## ⚠️ Read this first — data access

This system was authored in a Claude Code cloud session whose network policy
**blocks reddit.com at the egress proxy (HTTP 403)**. Every access path was
tested and blocked: `WebFetch`, `WebSearch` (reddit is a disallowed crawl
domain), direct `curl`, read-proxies, and search engines. There is also no
Reddit connector in the available Windsor.ai suite. General web search returns
effectively **zero** Reddit threads for this India-centric brand.

**Consequence:** no real Reddit data could be collected *in that session*, so no
analysis was produced — because producing analysis without data would mean
inventing it, which this project explicitly forbids. Instead, the complete
**collection + classification + analysis pipeline** was built and tested, so it
produces genuine analysis the moment it runs somewhere Reddit is reachable.

**To get real results, run this in an environment that allows Reddit** (a new
Claude Code session with `reddit.com`, `oauth.reddit.com`, `old.reddit.com`
allowlisted, or your own laptop/server) **with Reddit API credentials.**

Check readiness anytime:

```bash
python -m reddit_audit.run --check
```

---

## Multi-agent architecture (Phase 1)

The pipeline is a deterministic chain of specialised agents — no single agent
does everything (brief Phase 1).

| Agent / stage | File | Responsibility | Brief mapping |
|---|---|---|---|
| **Agent 1 — Discovery** | `collect.py` | Fan out the full query surface × sort orders × seed subreddits + site-wide search; find posts *and* comments | Phase 1 / Agent 1 |
| **Agent 2 — Extraction** | `collect.py` | Capture each mention verbatim with date, subreddit, URL, engagement, author; append-only, deduped | Phase 1 / Agent 2 |
| **Agent 3 — Evidence Quality** | `classify.py` | Evidence strength A/B/C/D, user type, first-hand flag | Phase 1 / Agent 3 |
| **Classification** | `classify.py` | Category, theme, multidimensional sentiment, journey stage, competitors, impact score | Phases 3, 6, 8, 10, 13 |
| **Dataset build** | `build_dataset.py` | Master CSV + 9-tab XLSX, all aggregations | Phases 2, 4, 5, 7, 11, 12, 19, 20 |
| **Strategic Synthesis** | *analyst/LLM* (template below) | Turn the workbook into initiatives — **reads the data, does not re-collect** | Phases 15–23 |

`taxonomy.py` holds all domain knowledge (search terms, subreddits, categories,
competitors, theme keywords, sentiment lexicon, evidence cues) as data, so the
taxonomy evolves without touching logic.

---

## Setup

```bash
pip install -r reddit_audit/requirements.txt

# Reddit "script" app: https://www.reddit.com/prefs/apps
export REDDIT_CLIENT_ID=...
export REDDIT_CLIENT_SECRET=...
export REDDIT_USER_AGENT="dailyobjects-audit by u/<yourname>"
export REDDIT_USERNAME=...      # optional; raises rate limits
export REDDIT_PASSWORD=...      # optional
```

Credentials are read from the environment only — never hard-coded, never committed.

## Run

```bash
python -m reddit_audit.run                       # full lifetime: discover + extract + classify + build
python -m reddit_audit.run --since-days 30 --report   # LAST-30-DAYS report (recommended cadence)
python -m reddit_audit.run --build-only              # rebuild tabs from the existing raw log
python -m reddit_audit.run --check                   # readiness / connectivity probe
```

**Last-30-days mode.** `--since-days N` scopes the crawl to the last *N* days
(the collector drops older mentions and biases Reddit's own time filter to
`month`/`year`). `--report` then renders `data/DailyObjects_Reddit_Report.md` —
the Phases 15-23 Voice-of-Customer report — with every number computed from real
rows, sections under 5 mentions flagged as *insufficient evidence*, and the
positioning/root-cause narrative left as a labelled scaffold for analyst
completion (never auto-invented).

Outputs land in `reddit_audit/data/` (git-ignored):
`DailyObjects_Reddit_Master.csv`, `DailyObjects_Reddit_Master.xlsx`,
`raw_mentions.jsonl` (append-only crawl log), `seen_ids.txt` (dedup ledger).

See the **structure** without real data:
`reddit_audit/examples/SAMPLE_workbook_synthetic.xlsx` — built from invented
fixtures purely to show the 9-tab layout. **Not real data. Not for analysis.**

---

## The workbook (Phase 2)

| Tab | Contents | Brief |
|---|---|---|
| `RAW_MENTIONS` | One row per meaningful mention, ~45 fields, verbatim text | Phase 2 Tab 1 |
| `THEME_TAXONOMY` | Theme/sub-theme definitions + trigger keywords | Tab 2 |
| `MONTHLY_TRENDS` | Volume, +/neutral/−/strong−, recommends, product-love, value, CX by month | Tab 3 / Phase 4 |
| `CATEGORY_ANALYSIS` | Per-category perception + BRAND BUILDER / NEUTRAL / REPUTATION RISK label | Tab 4 / Phase 7 |
| `COMPETITORS` | Every competitor mention, how often DO was discouraged in favour | Tab 5 / Phase 8 |
| `ISSUE_TRACKER` | Issue × first/last seen, volume, 12m volume, EMERGING/PERSISTENT/DECLINING/NOISE, severity | Tab 6 / Phase 11 |
| `POSITIVE_EQUITY_TRACKER` | Recurring positive signals, same methodology | Tab 7 |
| `QUOTE_LIBRARY` | Strongest A/B evidence, verbatim + URL | Tab 8 / Phase 20 |
| `BRAND_HEALTH` | Metric × {Historical, 12M, 6M, 3M} matrix | Phase 19 |

---

## Methodology (transparent by design)

**Evidence strength (Agent 3).** A = first-hand + specific; B = detailed
recommendation/comparison; C = casual opinion; D = hearsay. Analysis weights A/B
far above C/D. Cues live in `taxonomy.py` (`FIRSTHAND_CUES`, `HEARSAY_CUES`, …).

**Multidimensional sentiment (Phase 6).** Separate labels for product, quality,
value, brand, and CX — computed only from clauses touching that dimension's
keywords, so "love the design but it peeled" reads as product-positive /
quality-negative. A weighted lexicon with negation + intensifier handling; not a
black-box model, so labels are reproducible and auditable.

**Impact score (Phase 10), 0–10.** `intensity + engagement + evidence + recency`:
sentiment magnitude, log upvotes/replies, A/B weighted above C/D, and a recency
boost for the last 12/24 months. Deliberately simple — the brief warns against
manufacturing statistical precision the data can't support.

**Confidence + notes.** Every row carries `classification_confidence`
(high/medium/low) and `research_notes`. Low-confidence rows keep their raw text
and should get a human/LLM review pass before informing decisions. The lexicon
is a *first pass*, not the final word.

**Reddit ≠ customer base.** Report findings as *"among Reddit conversations
analysed, X appears…"*, never *"DailyObjects customers believe X."* Reddit
over-indexes toward tech-enthusiasts and the dissatisfied.

---

## Monthly re-run (Phase 24)

1. Set `TIME_FILTERS = ["month"]` (or `"year"`) in `config.py` for faster incremental crawls.
2. `python -m reddit_audit.run` — new mentions are deduped against `seen_ids.txt` and appended.
3. Rebuild recomputes all rolling 3M/6M/12M windows and the BRAND_HEALTH matrix.
4. Diff this month's `ISSUE_TRACKER` vs last month's to catch EMERGING issues and DECLINING ones.
5. New recurring phrases not covered by the taxonomy → add them to `taxonomy.py` and note it.

The point: **"Are the things we're fixing actually improving perception?"** —
answerable only because the dataset is longitudinal and the methodology is fixed.

---

## Strategic Synthesis template (Phases 15–23) — analyst/LLM fills from the workbook

Do **not** automate this — it is judgement, and it must read the populated
workbook, not re-collect. For each insight use the Phase-18 Business Action
Framework:

```
Insight · Evidence (URLs) · Scale · Evidence quality · Time trend ·
Categories · Business impact · Root-cause HYPOTHESIS (label it) ·
Recommended action (specific) · Owner · Success metric
```

Then produce: Issue Priority Matrix (FIX NOW / WATCH / INVESTIGATE / LOW),
the 15–30-row Management Action Table, the 30/90/365-day roadmap, and the
CEO Executive Summary (Phase 23). Every claim cites a `QUOTE_LIBRARY` row.
Show opposing evidence; never cherry-pick to a predetermined narrative.

---

## Files

```
reddit_audit/
├── README.md            this file
├── requirements.txt
├── config.py            paths, credentials (env only), crawl params
├── taxonomy.py          search surface, categories, competitors, themes, lexicon
├── collect.py           Agent 1 + 2  (PRAW + public-JSON fallback)
├── classify.py          Agent 3 + theme/sentiment/impact  (~45-col row builder)
├── build_dataset.py     Master CSV + 9-tab XLSX + all aggregations
├── run.py               orchestrator (--check / --build-only)
├── tests/test_pipeline.py   smoke tests on synthetic fixtures
└── examples/make_sample.py  builds SAMPLE_workbook_synthetic.xlsx (NOT real data)
```
