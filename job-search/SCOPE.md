# Job Search Tool — Scope (v1)

Personal, local-first web app that finds India-based roles and roles at a watchlist
of target companies, ranks them against my resume with AI, tracks applications,
sends a daily digest, and tailors resumes/cover letters per job.

## Decisions
| Area | Decision |
|---|---|
| User | Single user (me), runs locally, no auth |
| Market | India-based roles + a watchlist of specific companies |
| Interface | Local web app |
| v1 features | AI fit scoring, application tracker, daily digest, resume/cover-letter tailoring |
| Out of scope | Auto-apply; scraping LinkedIn/Naukri (ToS / account bans) — use manual paste-in instead |

## Stack
- Python 3.11+, SQLite (via SQLModel)
- Streamlit UI (multi-page)
- Claude API (Anthropic SDK) for scoring + tailoring
- APScheduler / cron for the daily fetch + digest
- Digest via email (SMTP / Gmail app password) and an in-app "Today" page

## Job sources
1. **Adzuna API (India, `in`)** — free API key; keyword + location search.
2. **Company watchlist via public ATS APIs** — no auth needed:
   - Greenhouse: `boards-api.greenhouse.io/v1/boards/{company}/jobs`
   - Lever: `api.lever.co/v0/postings/{company}`
   - Ashby: `api.ashbyhq.com/posting-api/job-board/{company}`
   - Others (Workday, custom pages): manual add for now.
3. **Manual add** — paste a URL + job description (LinkedIn, Naukri, Instahyre, referrals).

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
- `job` (normalised fields, source, external_id, hash, first_seen, status)
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
    sources/ adzuna.py greenhouse.py lever.py ashby.py manual.py
    pipeline.py          # fetch → dedupe → filter → score
    ai.py                # scoring + tailoring prompts
    digest.py scheduler.py
  tests/
  .env.example           # ANTHROPIC_API_KEY, ADZUNA_APP_ID/KEY, SMTP_*
```

## Build plan
1. **Foundation** — project skeleton, models/DB, config, Profile + Companies pages.
2. **Ingestion** — Adzuna + Greenhouse/Lever/Ashby + manual add; dedupe; Jobs page.
3. **AI scoring** — scoring prompt, caching, ranked Jobs view with explanations.
4. **Tracker** — stages, notes, follow-ups.
5. **Tailoring** — resume/cover letter generation + export.
6. **Digest** — scheduler + email + Today page.

## Needed from me before/during build
- Anthropic API key, Adzuna app id/key (free at developer.adzuna.com)
- Resume file, target roles/cities/CTC, company watchlist
- Email for digest (+ SMTP/Gmail app password) — optional
