"""Settings loaded from environment / .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def _int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    db_path: Path
    first_sync_days: int
    max_job_age_days: int
    archive_after_days: int
    anthropic_api_key: str
    serpapi_key: str
    serpapi_queries_per_run: int
    serpapi_monthly_limit: int
    adzuna_app_id: str
    adzuna_app_key: str
    gmail_credentials_file: Path
    smtp_user: str
    digest_to: str

    def missing_keys(self) -> dict[str, bool]:
        """Which integrations are configured (True) or not (False)."""
        return {
            "Anthropic (AI scoring & tailoring)": bool(self.anthropic_api_key),
            "SerpAPI (Google Jobs)": bool(self.serpapi_key),
            "Adzuna": bool(self.adzuna_app_id and self.adzuna_app_key),
            "Gmail (portal alert emails)": self.gmail_credentials_file.exists(),
            "Digest email (SMTP)": bool(self.smtp_user and self.digest_to),
        }


def load_settings() -> Settings:
    db_path = Path(os.getenv("JOBSEARCH_DB_PATH", "data/jobsearch.db"))
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    creds = Path(os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"))
    if not creds.is_absolute():
        creds = PROJECT_ROOT / creds
    return Settings(
        db_path=db_path,
        first_sync_days=_int("FIRST_SYNC_DAYS", 7),
        max_job_age_days=_int("MAX_JOB_AGE_DAYS", 21),
        archive_after_days=_int("ARCHIVE_AFTER_DAYS", 14),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        serpapi_key=os.getenv("SERPAPI_KEY", ""),
        serpapi_queries_per_run=_int("SERPAPI_QUERIES_PER_RUN", 3),
        serpapi_monthly_limit=_int("SERPAPI_MONTHLY_LIMIT", 100),
        adzuna_app_id=os.getenv("ADZUNA_APP_ID", ""),
        adzuna_app_key=os.getenv("ADZUNA_APP_KEY", ""),
        gmail_credentials_file=creds,
        smtp_user=os.getenv("SMTP_USER", ""),
        digest_to=os.getenv("DIGEST_TO", ""),
    )


ENV_PATH = PROJECT_ROOT / ".env"


def save_env(values: dict[str, str], path: Path = ENV_PATH) -> None:
    """Update keys in .env (keeping other lines and comments) and in this process."""
    lines = path.read_text().splitlines() if path.exists() else []
    remaining = dict(values)
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip()
        if not line.lstrip().startswith("#") and "=" in line and key in remaining:
            lines[i] = f"{key}={remaining.pop(key)}"
    lines += [f"{k}={v}" for k, v in remaining.items()]
    path.write_text("\n".join(lines) + "\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    os.environ.update(values)
