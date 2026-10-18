from jobsearch.profile import get_profile, is_complete, split_list, update_profile


def test_split_list_trims_and_dedupes():
    assert split_list(" Bengaluru, mumbai\nBENGALURU,, \nPune ") == ["Bengaluru", "mumbai", "Pune"]
    assert split_list("") == []


def test_get_profile_creates_single_row(session):
    a = get_profile(session)
    b = get_profile(session)
    assert a.id == b.id


def test_version_changes_with_resume_and_prefs(session):
    p = update_profile(session, target_titles=["PM"], resume_text="x" * 300)
    v1 = p.resume_version
    assert v1
    assert update_profile(session, full_name="Ankit").resume_version == v1  # name doesn't affect scoring
    assert update_profile(session, cities=["Pune"]).resume_version != v1


def test_is_complete(session):
    p = update_profile(session, target_titles=["PM"], remote_ok=False)
    assert not is_complete(p)
    p = update_profile(session, resume_text="x" * 300, cities=["Delhi"])
    assert is_complete(p)


def test_update_rejects_unknown_fields(session):
    import pytest

    with pytest.raises(ValueError):
        update_profile(session, bogus=1)
