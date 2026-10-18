from jobsearch.matching import matches_profile, title_matches
from jobsearch.models import Job, Profile


def job(title="Senior Category Manager", location="Gurugram, Haryana", remote=False, description=""):
    return Job(dedupe_hash="x", title=title, company="Acme", location=location, remote=remote,
               description=description)


def test_title_matches_core_words():
    assert title_matches("Senior Category Manager - Home", "Category Manager")
    assert title_matches("Manager, Categories", "Category Manager")
    assert not title_matches("Engineering Manager", "Category Manager")
    assert title_matches("Head of Growth", "Head of Growth")


def test_profile_filters():
    p = Profile(target_titles=["Category Manager"], cities=["Gurgaon", "Delhi"],
                remote_ok=True, deal_breakers=["night shift"])
    assert matches_profile(job(), p)[0]
    assert matches_profile(job(location="Mumbai"), p) == (False, "location")
    assert matches_profile(job(location="Mumbai", remote=True), p)[0]
    assert matches_profile(job(location="India"), p)[0]
    assert matches_profile(job(title="Data Engineer"), p) == (False, "title")
    assert matches_profile(job(description="Rotational night shift"), p)[1].startswith("deal-breaker")


def test_empty_profile_matches_everything():
    assert matches_profile(job(title="Anything", location="Mumbai"), Profile())[0]
