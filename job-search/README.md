# Job Search

A personal job-search tool that runs on your machine. It pulls jobs from Naukri, iimjobs and
LinkedIn alert emails, Google Jobs, Adzuna and company careers pages, then scores, tracks and
tailors applications. See [SCOPE.md](SCOPE.md) for the full plan.

## Status
- [x] Step 1: Foundation: database, Profile page (resume upload), Company watchlist
- [x] Step 2a: Ingestion: company boards (Greenhouse/Lever/Ashby), Google Jobs (SerpAPI), Adzuna,
      manual add, merging duplicates, freshness filter, closed-job detection, Jobs page, Settings page
- [ ] Step 2b: Naukri / iimjobs / LinkedIn alert emails from Gmail (needs sample emails)
- [ ] Step 3: AI fit scoring
- [ ] Step 4: Application tracker
- [ ] Step 5: Resume & cover-letter tailoring
- [ ] Step 6: Daily digest

## Run it
**macOS / Linux:** open a terminal in the `job-search` folder and run `./run.sh`
**Windows:** double-click `run.bat`

The first run sets everything up (about a minute). After that the app opens in your browser at
http://localhost:8501. It is only reachable from your own computer.

Then:
1. **Profile:** upload your resume and set target roles and cities.
2. **Companies:** paste careers-page links for companies you want to watch.
3. **Settings:** paste your SerpAPI and Adzuna keys.
4. **Jobs:** click *Fetch new jobs now*.

Fetch from the command line or a scheduled task instead: `.venv/bin/python -m jobsearch.fetch`

Your data lives in `data/jobsearch.db` and your keys in `.env`. Neither is ever committed.

### Getting the free API keys
- **SerpAPI:** sign up at https://serpapi.com/users/sign_up, verify your email, then copy
  *Your Private API Key* from the dashboard. The free plan gives 100 searches a month; the app
  uses at most 3 per fetch.
- **Adzuna:** register at https://developer.adzuna.com/signup, then open *Dashboard → API Access
  Details* and copy the **Application ID** and **Application Key**.

## Tests
```bash
python -m pytest -q
```
