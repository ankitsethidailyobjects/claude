import streamlit as st

from jobsearch.companies import list_companies
from jobsearch.config import load_settings
from jobsearch.db import session_scope
from jobsearch.profile import get_profile, is_complete

settings = load_settings()

st.title("🔎 Job Search")
st.caption("Naukri · iimjobs · LinkedIn alerts · Google Jobs · Adzuna · company careers pages")

with session_scope() as session:
    profile = get_profile(session)
    companies = list_companies(session)

st.subheader("Setup")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Your data**")
    st.markdown(f"{'✅' if profile.resume_text else '⬜'} Resume uploaded")
    st.markdown(f"{'✅' if profile.target_titles else '⬜'} Target roles set")
    st.markdown(f"{'✅' if (profile.cities or profile.remote_ok) else '⬜'} Locations set")
    active = sum(c.active for c in companies)
    st.markdown(f"{'✅' if companies else '⬜'} Company watchlist ({active} active)")
    if not is_complete(profile):
        st.page_link("views/profile.py", label="Complete your profile →", icon="👤")
with col2:
    st.markdown("**Integrations** (set in `.env`)")
    for name, ok in settings.missing_keys().items():
        st.markdown(f"{'✅' if ok else '⬜'} {name}")

st.subheader("Freshness rules")
st.markdown(
    f"- First Gmail sync reads alerts from the last **{settings.first_sync_days} days** only\n"
    f"- Jobs older than **{settings.max_job_age_days} days** are hidden and not scored\n"
    f"- Jobs not seen for **{settings.archive_after_days} days** are archived "
    "(unless saved or applied)"
)
st.caption("Change these in `.env` (FIRST_SYNC_DAYS, MAX_JOB_AGE_DAYS, ARCHIVE_AFTER_DAYS).")
