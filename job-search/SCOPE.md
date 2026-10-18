# Job Search Tool — Scope (v1)

Personal, local-first web app that pulls jobs from Naukri, iimjobs and LinkedIn
(plus Google Jobs, Adzuna and a watchlist of target companies), ranks them against my resume with AI, tracks applications,
sends a daily digest, and tailors resumes/cover letters per job.

## Decisions
| Area | Decision |
|---|---|
| User | Single user (me), runs locally, no auth |
| Market | India-based roles + a watchlist of specific companies |
| Primary portals | Naukri, iimjobs, LinkedIn — via job-alert emails + Google Jobs (SerpAPI) |
| Interface | Local web app |
| v1 features | AI fit scoring, application tracker, daily digest, resume/cover-letter tailoring |
| Out of scope | Auto-apply; direct scraping of Naukri/iimjobs/LinkedIn (ToS, anti-bot, account-ban risk) |

## Stack
- Python 3.11+, SQLite (via SQLModel)
- Streamlit UI (multi-page)
- Claude API (Anthropic SDK) for scoring + tailoring
- APScheduler / cron for the daily fetch + digest
- Digest via email (SMTP / Gmail app password) and an in-app "Today" page

## Job sources
1. **Portal job-alert emails (primary)** — create saved-search alerts on Naukri, iimjobs and
   LinkedIn; the tool reads them from Gmail (Gmail API, read-only scope, filtered by sender)
   and parses each listing (title, company, location, experience, CTC, link).
   - One parser per portal: `naukri`, `iimjobs`, `linkedin`; raw emails kept so parsers can be
     fixed and re-run when a template changes.
   - Optional: fetch the public job page by link to get the full description for scoring
     (low volume, one page per job, fall back to the email snippet if blocked).
2. **Google Jobs via SerpAPI** — `engine=google_jobs`, `gl=in`, queries built from target
   titles × cities; Google indexes Naukri/LinkedIn/iimjobs/company listings. Free tier ≈100
   searches/month, so queries are budgeted (e.g. 3/day).
3. **Adzuna API (India, `in`)** — free API key; keyword + location search.
4. **Company watchlist via public ATS APIs** — no auth needed:
   - Greenhouse: `boards-api.greenhouse.io/v1/boards/{company}/jobs`
   - Lever: `api.lever.co/v0/postings/{company}`
   - Ashby: `api.ashbyhq.com/posting-api/job-board/{company}`
5. **Manual add** — paste a URL + job description (referrals, anything else).

The same job often arrives from several sources (e.g. a LinkedIn alert and Google Jobs);
dedupe merges them and records every source + link.

## Freshness (keeping old listings out)
1. **Only recent emails are read.** The first run reads alert emails from the last 7 days
   (Gmail query `newer_than:7d`, configurable). Each later run reads only mail that arrived
   since the last sync. Processed message IDs are stored, so no email is parsed twice.
   The older backlog in the inbox is never touched.
2. **Every job gets a best-estimate posting date**, taken from the first of these available:
   the "posted X days ago" text in the email or job page; SerpAPI's `posted_at`; the ATS
   `created_at`/`updated_at`; otherwise the date the alert email arrived (a ceiling on age).
3. **Age cut-off.** Jobs older than a max age (default 21 days, configurable) are hidden
   from the Jobs page and the digest, and are not sent for AI scoring.
4. **Liveness check before it matters.** Before a job goes into the digest or gets a tailored
   resume, its link is checked once: 404, a redirect to search results, or text like
   "no longer accepting applications" / "job expired" marks it **Closed**. If the portal
   blocks the check, the job is marked **Unverified** rather than guessed.
   - Watchlist (Greenhouse/Lever/Ashby) jobs: a job that drops out of the company's feed is
     marked Closed automatically.
5. **Last-seen tracking.** Each time a job reappears in a new alert or search, `last_seen` is
   updated. Jobs not seen for 14 days and not saved/applied are auto-archived.
6. **In the UI:** a freshness badge (New today · 3d · 2w · Closed · Unverified), a max-age
   filter, and ranking that combines fit score with freshness. Saved/applied jobs are never
   auto-archived.

## Features
### 1. Profile & preferences
- Upload resume (PDF/DOCX → text), target titles, seniority, cities (+ remote OK?),
  min CTC, must-have / deal-breaker keywords, company watchlist (name + ATS + slug).

### 2. Ingestion & dedupe
- Fetchers per source normalise to one `Job` schema
  (title, company, location, remote, salary, description, url, source, posted_at).
- Dedupe on normalised (company, title, location) + URL hash.
- Cheap rule-based pre-filter (title/location/keywords/age) before any AI calls.

### 3. AI fit scoring
- Claude scores each new filtered job vs resume + preferences → JSON:
  `score 0–100`, `summary`, `why_fit[]`, `gaps[]`, `red_flags[]`, `salary_signal`.
- Cached per (job, resume version); re-score only when resume/preferences change.
- Prompt caching on the resume/preferences block to keep cost low.

### 4. Application tracker
- Kanban/table: Saved → Applied → Interviewing → Offer / Rejected / Withdrawn.
- Per job: notes, contacts, applied date, next follow-up date, attached tailored docs.

### 5. Daily digest
- Scheduled run: fetch → dedupe → filter → score → email top N new matches
  (score ≥ threshold) + follow-ups due today.

### 6. Resume & cover-letter tailoring
- For a selected job: tailored resume bullets (reorder/rephrase, never invent experience),
  cover letter, and a short "why me" pitch. Export as DOCX/Markdown.

## Data model (SQLite)
- `profile` (single row: prefs JSON, resume text, resume_version)
- `company_watch` (name, ats, slug, active)
- `job` (normalised fields, hash, posted_at, posted_at_source, first_seen, last_seen,
  liveness: open|closed|unverified, liveness_checked_at, status)
- `job_source` (job_id, source, external_id, url, seen_at) — one job, many portals
- `raw_email` (gmail_id, portal, received_at, html, parsed_ok)
- `sync_state` (source, last_synced_at / last Gmail history id)
- `job_score` (job_id, resume_version, score, analysis JSON, created_at)
- `application` (job_id, stage, applied_at, follow_up_at, notes)
- `document` (job_id, type resume|cover, content, created_at)

## Project layout
```
job-search/
  app.py                 # Streamlit entry
  pages/                 # Today, Jobs, Tracker, Profile, Companies
  jobsearch/
    db.py models.py config.py
    sources/ gmail_alerts.py serpapi_jobs.py adzuna.py greenhouse.py lever.py ashby.py manual.py
    parsers/ naukri.py iimjobs.py linkedin.py   # alert-email parsers
    pipeline.py          # fetch → dedupe → filter → score
    ai.py                # scoring + tailoring prompts
    digest.py scheduler.py
  tests/
  .env.example           # ANTHROPIC_API_KEY, SERPAPI_KEY, ADZUNA_APP_ID/KEY, GMAIL creds, SMTP_*
```

## Build plan
1. **Foundation** — project skeleton, models/DB, config, Profile + Companies pages.
2. **Ingestion** — Gmail alert parsers (Naukri, iimjobs, LinkedIn) + SerpAPI + Adzuna +
   Greenhouse/Lever/Ashby + manual add; dedupe; Jobs page.
3. **AI scoring** — scoring prompt, caching, ranked Jobs view with explanations.
4. **Tracker** — stages, notes, follow-ups.
5. **Tailoring** — resume/cover letter generation + export.
6. **Digest** — scheduler + email + Today page.

## Needed from me before/during build
- Anthropic API key, Adzuna app id/key (free at developer.adzuna.com),
  SerpAPI key (free tier at serpapi.com)
- Job alerts set up on Naukri, iimjobs and LinkedIn, delivered to one Gmail account
- Google Cloud OAuth client (Desktop app) with Gmail API enabled, read-only scope
- 2–3 sample alert emails from each portal (to build and test the parsers)
- Resume file, target roles/cities/CTC, company watchlist
- Email for digest (+ SMTP/Gmail app password) — optional
