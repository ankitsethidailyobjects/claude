import streamlit as st

from jobsearch.config import ENV_PATH, load_settings, save_env

st.title("⚙️ Settings")
st.caption(f"Saved to `{ENV_PATH}` on this computer only. Never committed to git.")

settings = load_settings()


def masked(value: str) -> str:
    return f"saved (…{value[-4:]})" if value else "not set"


with st.form("keys"):
    st.markdown("**SerpAPI — Google Jobs** (covers Naukri, LinkedIn, iimjobs listings)")
    st.caption("Sign up free at serpapi.com → Dashboard → copy *Your Private API Key*. "
               f"Currently: {masked(settings.serpapi_key)}")
    serpapi = st.text_input("SerpAPI key", type="password", placeholder="leave blank to keep current")

    st.markdown("**Adzuna**")
    st.caption("Register free at developer.adzuna.com → Dashboard → *API Access Details*. "
               f"Currently: ID {masked(settings.adzuna_app_id)}, key {masked(settings.adzuna_app_key)}")
    a1, a2 = st.columns(2)
    adzuna_id = a1.text_input("Adzuna app ID", placeholder="leave blank to keep current")
    adzuna_key = a2.text_input("Adzuna app key", type="password", placeholder="leave blank to keep current")

    st.markdown("**Anthropic — AI scoring & tailoring** (used from step 3)")
    st.caption(f"console.anthropic.com → API Keys. Currently: {masked(settings.anthropic_api_key)}")
    anthropic = st.text_input("Anthropic API key", type="password", placeholder="leave blank to keep current")

    st.markdown("**Freshness**")
    f1, f2, f3, f4 = st.columns(4)
    first_sync = f1.number_input("First Gmail sync (days)", 1, 90, settings.first_sync_days)
    max_age = f2.number_input("Max job age (days)", 1, 90, settings.max_job_age_days)
    archive = f3.number_input("Archive after not seen (days)", 1, 90, settings.archive_after_days)
    per_run = f4.number_input("Google Jobs searches per fetch", 0, 20, settings.serpapi_queries_per_run)

    if st.form_submit_button("Save", type="primary"):
        values = {
            "FIRST_SYNC_DAYS": str(first_sync),
            "MAX_JOB_AGE_DAYS": str(max_age),
            "ARCHIVE_AFTER_DAYS": str(archive),
            "SERPAPI_QUERIES_PER_RUN": str(per_run),
        }
        for env_key, val in {"SERPAPI_KEY": serpapi, "ADZUNA_APP_ID": adzuna_id,
                             "ADZUNA_APP_KEY": adzuna_key, "ANTHROPIC_API_KEY": anthropic}.items():
            if val.strip():
                values[env_key] = val.strip()
        save_env(values)
        st.success("Saved.")
        st.rerun()
