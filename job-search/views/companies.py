import streamlit as st

from jobsearch.companies import (
    BoardNotFound,
    WatchlistError,
    add_company,
    fetch_board,
    list_companies,
    parse_careers_url,
    remove_company,
    set_active,
)
from jobsearch.db import session_scope

st.title("🏢 Company watchlist")
st.caption(
    "Companies whose careers pages run on Greenhouse, Lever or Ashby. Their jobs are pulled "
    "directly, and a job that disappears from their board is marked Closed."
)

with st.form("add_company", clear_on_submit=True):
    st.markdown("**Add a company**")
    c1, c2 = st.columns([1, 2])
    name = c1.text_input("Company name", placeholder="Razorpay")
    url = c2.text_input("Careers page URL", placeholder="https://jobs.lever.co/razorpay")
    check = st.checkbox("Check the board exists before adding", value=True)
    submitted = st.form_submit_button("Add", type="primary")

if submitted:
    try:
        ats, slug = parse_careers_url(url)
        count, warning = None, None
        if check:
            try:
                count = len(fetch_board(ats, slug))
            except BoardNotFound:
                raise
            except WatchlistError as e:
                # Network trouble shouldn't block adding; the daily fetch will retry.
                warning = f"Added without checking: {e}"
        with session_scope() as session:
            add_company(session, name or slug.title(), ats, slug)
        msg = f"Added {name or slug} ({ats.value}/{slug})"
        if warning:
            st.warning(warning)
        else:
            st.success(msg + (f" — {count} open jobs right now." if count is not None else "."))
    except WatchlistError as e:
        st.error(str(e))

with st.expander("Careers page not a link like that?"):
    st.markdown(
        "Open the company's careers page and click any job. If the address contains "
        "`greenhouse.io`, `lever.co` or `ashbyhq.com`, paste that link above. "
        "Otherwise the company uses a different system (e.g. Workday, Darwinbox) — "
        "you'll still catch its jobs through Naukri/LinkedIn alerts and Google Jobs."
    )

with session_scope() as session:
    companies = list_companies(session)

st.subheader(f"Watching {sum(c.active for c in companies)} of {len(companies)}")
if not companies:
    st.info("No companies yet.")
for company in companies:
    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
    c1.markdown(f"**{company.name}**")
    c2.markdown(f"`{company.ats.value}/{company.slug}`")
    active = c3.toggle("Active", company.active, key=f"active-{company.id}")
    if active != company.active:
        with session_scope() as session:
            set_active(session, company.id, active)
        st.rerun()
    if c4.button("Remove", key=f"rm-{company.id}"):
        with session_scope() as session:
            remove_company(session, company.id)
        st.rerun()
