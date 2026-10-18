# Job Search

A personal job-search tool that runs on your machine. It pulls jobs from Naukri, iimjobs and
LinkedIn alert emails, Google Jobs, Adzuna and company careers pages, then scores, tracks and
tailors applications. See [SCOPE.md](SCOPE.md) for the full plan.

## Status
- [x] Step 1: Foundation: database, Profile page (resume upload), Company watchlist
- [ ] Step 2: Ingestion (Gmail alerts, SerpAPI, Adzuna, Greenhouse/Lever/Ashby, manual add)
- [ ] Step 3: AI fit scoring
- [ ] Step 4: Application tracker
- [ ] Step 5: Resume & cover-letter tailoring
- [ ] Step 6: Daily digest

## Run it
```bash
cd job-search
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in keys as later steps need them
streamlit run app.py
```
The app opens at http://localhost:8501. Data is stored in `data/jobsearch.db`, which is never committed.

## Tests
```bash
python -m pytest -q
```
