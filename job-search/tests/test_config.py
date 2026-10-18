import os

from jobsearch.config import save_env


def test_save_env_updates_in_place(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("# comment\nSERPAPI_KEY=\nMAX_JOB_AGE_DAYS=21\n")
    monkeypatch.delenv("SERPAPI_KEY", raising=False)
    save_env({"SERPAPI_KEY": "abc", "ADZUNA_APP_ID": "id1"}, path)
    assert path.read_text() == "# comment\nSERPAPI_KEY=abc\nMAX_JOB_AGE_DAYS=21\nADZUNA_APP_ID=id1\n"
    assert os.environ["SERPAPI_KEY"] == "abc"
    monkeypatch.delenv("ADZUNA_APP_ID")
