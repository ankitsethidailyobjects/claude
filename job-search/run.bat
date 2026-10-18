@echo off
REM One-click start on Windows: double-click run.bat
cd /d "%~dp0"
if not exist .venv (
  echo First run: setting up, takes a minute...
  python -m venv .venv
)
.venv\Scripts\pip install -q -r requirements.txt
if not exist .env copy .env.example .env
.venv\Scripts\streamlit run app.py
