import streamlit as st

from jobsearch.db import session_scope
from jobsearch.profile import get_profile, split_list, update_profile
from jobsearch.resume import ResumeError, extract_text

SENIORITY = ["", "Entry", "Mid", "Senior", "Lead / Manager", "Director", "VP / Head", "CXO"]

st.title("👤 Profile")
st.caption("Used to filter and score jobs, and to tailor your resume.")

with session_scope() as session:
    profile = get_profile(session)

with st.form("profile"):
    full_name = st.text_input("Full name", profile.full_name)
    titles = st.text_area(
        "Target job titles (one per line or comma separated)",
        "\n".join(profile.target_titles),
        placeholder="Category Manager\nHead of Growth\nProduct Manager",
    )
    c1, c2, c3 = st.columns(3)
    seniority = c1.selectbox(
        "Seniority",
        SENIORITY,
        index=SENIORITY.index(profile.seniority) if profile.seniority in SENIORITY else 0,
    )
    years = c2.number_input(
        "Years of experience", min_value=0.0, max_value=50.0, step=0.5,
        value=float(profile.years_experience or 0),
    )
    min_ctc = c3.number_input(
        "Minimum CTC (₹ LPA, 0 = no minimum)", min_value=0.0, step=1.0,
        value=float(profile.min_ctc_lpa or 0),
    )
    c4, c5 = st.columns([3, 1])
    cities = c4.text_input(
        "Cities", ", ".join(profile.cities), placeholder="Bengaluru, Gurugram, Mumbai"
    )
    remote_ok = c5.checkbox("Open to remote", profile.remote_ok)
    must = st.text_input(
        "Must-have keywords (optional)", ", ".join(profile.must_have_keywords),
        placeholder="D2C, e-commerce, P&L",
    )
    breakers = st.text_input(
        "Deal-breakers (optional)", ", ".join(profile.deal_breakers),
        placeholder="night shift, BPO, commission only",
    )
    upload = st.file_uploader(
        "Resume (PDF, DOCX or TXT)" + (f" — current: {profile.resume_filename}" if profile.resume_filename else ""),
        type=["pdf", "docx", "txt", "md"],
    )
    submitted = st.form_submit_button("Save profile", type="primary")

if submitted:
    changes = dict(
        full_name=full_name.strip(),
        target_titles=split_list(titles),
        seniority=seniority,
        years_experience=years or None,
        min_ctc_lpa=min_ctc or None,
        cities=split_list(cities),
        remote_ok=remote_ok,
        must_have_keywords=split_list(must),
        deal_breakers=split_list(breakers),
    )
    error = None
    if upload is not None:
        try:
            changes["resume_text"] = extract_text(upload.name, upload.getvalue())
            changes["resume_filename"] = upload.name
        except ResumeError as e:
            error = str(e)
    if error:
        st.error(error)
    else:
        with session_scope() as session:
            profile = update_profile(session, **changes)
        st.success(f"Saved. Profile version `{profile.resume_version}`.")

if profile.resume_text:
    with st.expander(f"Resume text read from {profile.resume_filename} ({len(profile.resume_text):,} characters)"):
        st.caption("This is what the AI will see. If something important is missing, upload a DOCX instead.")
        st.text(profile.resume_text)
