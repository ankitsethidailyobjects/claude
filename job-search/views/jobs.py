from datetime import date, datetime, time, timezone

import pandas as pd
import streamlit as st
from sqlmodel import select

from jobsearch.config import load_settings
from jobsearch.db import session_scope
from jobsearch.matching import matches_profile
from jobsearch.models import Job, JobSource, JobStatus, Liveness
from jobsearch.pipeline import SourceReport, age_days, fetch_all, upsert_jobs
from jobsearch.profile import get_profile
from jobsearch.sources.manual import make_job

settings = load_settings()

st.title("💼 Jobs")

c1, c2 = st.columns([1, 3])
if c1.button("Fetch new jobs now", type="primary"):
    with st.spinner("Fetching from company boards, Google Jobs and Adzuna…"):
        with session_scope() as session:
            report = fetch_all(session, settings)
    st.session_state["last_report"] = report
report = st.session_state.get("last_report")
if report:
    with c2.expander(f"Last fetch: {report.new} new jobs, {report.archived} archived", expanded=False):
        for r in report.sources:
            line = f"**{r.source}**: {r.fetched} fetched · {r.new} new · {r.merged} merged · {r.too_old} too old"
            if r.closed:
                line += f" · {r.closed} closed"
            st.markdown(line)
            if r.error:
                st.error(r.error)
        if not settings.serpapi_key or not settings.adzuna_app_id:
            st.caption("Add SerpAPI / Adzuna keys on the Settings page to search the portals too.")

with st.expander("➕ Add a job manually (LinkedIn, Naukri, iimjobs, referral…)"):
    with st.form("manual", clear_on_submit=True):
        m1, m2, m3 = st.columns(3)
        title = m1.text_input("Job title")
        company = m2.text_input("Company")
        location = m3.text_input("Location")
        url = st.text_input("Link")
        description = st.text_area("Job description (paste the full text — used for AI scoring)", height=150)
        m4, m5 = st.columns(2)
        posted = m4.date_input("Posted on (if shown)", value=None, max_value=date.today())
        salary = m5.text_input("Salary / CTC (optional)")
        if st.form_submit_button("Add job"):
            try:
                posted_dt = datetime.combine(posted, time(12), tzinfo=timezone.utc) if posted else None
                nj = make_job(title, company, location, url, description, posted_dt, salary)
                r = SourceReport(source="manual")
                with session_scope() as session:
                    # Manual jobs are always kept, whatever their age.
                    upsert_jobs(session, [nj], max_age_days=36500, report=r)
                st.success("Added." if r.new else "Already in the list — merged the details.")
            except ValueError as e:
                st.error(str(e))

with session_scope() as session:
    profile = get_profile(session)
    jobs = list(session.exec(select(Job).where(Job.status != JobStatus.hidden)))
    sources: dict[int, list[str]] = {}
    for link in session.exec(select(JobSource)):
        sources.setdefault(link.job_id, []).append(link.source.split(":")[0])

with st.sidebar:
    st.markdown("### Filters")
    max_age = st.slider("Max age (days)", 1, 60, settings.max_job_age_days)
    only_match = st.toggle("Only jobs matching my profile", value=True)
    show_closed = st.toggle("Show closed jobs", value=False)
    show_archived = st.toggle("Show archived", value=False)
    query = st.text_input("Search title / company")
    all_sources = sorted({s for v in sources.values() for s in v})
    picked_sources = st.multiselect("Sources", all_sources, default=all_sources)


def badge(job: Job, age: int) -> str:
    if job.liveness == Liveness.closed:
        return "⛔ Closed"
    if age == 0:
        return "🟢 New today"
    if age <= 3:
        return f"🟢 {age}d"
    if age <= 10:
        return f"🟡 {age}d"
    return f"🟠 {age}d"


rows, hidden_by_profile = [], 0
for job in jobs:
    age = age_days(job)
    if age > max_age:
        continue
    if job.liveness == Liveness.closed and not show_closed:
        continue
    if job.status == JobStatus.archived and not show_archived:
        continue
    job_sources = sorted(set(sources.get(job.id, [])))
    if picked_sources is not None and all_sources and not set(job_sources) & set(picked_sources):
        continue
    if query and query.lower() not in f"{job.title} {job.company}".lower():
        continue
    if only_match:
        ok, _ = matches_profile(job, profile)
        if not ok:
            hidden_by_profile += 1
            continue
    rows.append({
        "Fresh": badge(job, age),
        "Age": age,
        "Title": job.title,
        "Company": job.company,
        "Location": ("🌐 " if job.remote else "") + job.location,
        "Salary": job.salary,
        "Sources": ", ".join(job_sources),
        "Link": job.url or None,
    })

st.subheader(f"{len(rows)} jobs")
if hidden_by_profile:
    st.caption(f"{hidden_by_profile} more hidden because they don't match your profile's titles, "
               "cities or deal-breakers (toggle in the sidebar).")
if not jobs:
    st.info("No jobs yet. Add companies to your watchlist and click **Fetch new jobs now**, "
            "or add your SerpAPI / Adzuna keys on the Settings page.")
elif rows:
    df = pd.DataFrame(rows).sort_values("Age")
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Age": None,
            "Link": st.column_config.LinkColumn("Link", display_text="Open ↗"),
        },
    )
