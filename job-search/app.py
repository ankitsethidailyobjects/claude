"""Streamlit entry point: `streamlit run app.py`."""

import streamlit as st

st.set_page_config(page_title="Job Search", page_icon="🔎", layout="wide")

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/profile.py", title="Profile", icon="👤"),
    st.Page("views/companies.py", title="Companies", icon="🏢"),
]

st.navigation(pages).run()
