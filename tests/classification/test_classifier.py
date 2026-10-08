"""Tests de classifier.py: pipeline FST -> orden -> DFA, para los 4 perfiles."""

import random

import pytest

from src.classification.classifier import (
    ACCEPTED, REJECTED, accepted_profiles, classify_candidate, classify_profile,
)
from src.normalization.normalizer import normalize_qualifications

PROFILES = ["FULL_STACK_DEVELOPER", "MACHINE_LEARNING_ENGINEER", "QA_ENGINEER", "DATA_ANALYST"]

CVS = {
    "FULL_STACK_DEVELOPER": ["JS", "React.js", "NodeJS", "Postgres", "Git"],           # PDF: Wednesday
    "MACHINE_LEARNING_ENGINEER": ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"],  # PDF: Mary Jane
    "QA_ENGINEER": ["pytest", "Selenium", "Postman", "Python", "Jira", "Git"],
    "DATA_ANALYST": ["SQL", "Excel", "Python", "pandas", "Power BI"],
}


def _classify(raw):
    return classify_candidate(normalize_qualifications(raw))


def test_result_has_the_four_profiles_and_valid_values():
    result = classify_candidate([])
    assert list(result) == PROFILES
    assert set(result.values()) == {REJECTED}


@pytest.mark.parametrize("profile", PROFILES)
def test_golden_cv_is_accepted_by_its_profile(profile):
    assert _classify(CVS[profile])[profile] == ACCEPTED


def test_wednesday_addams_only_full_stack():
    assert accepted_profiles(normalize_qualifications(CVS["FULL_STACK_DEVELOPER"])) == ["FULL_STACK_DEVELOPER"]


def test_mary_jane_watson_only_ml_engineer():
    assert accepted_profiles(normalize_qualifications(CVS["MACHINE_LEARNING_ENGINEER"])) == ["MACHINE_LEARNING_ENGINEER"]


@pytest.mark.parametrize("profile", PROFILES)
def test_input_order_does_not_change_result(profile):
    base = _classify(CVS[profile])
    for seed in range(10):
        raw = CVS[profile][:]
        random.Random(seed).shuffle(raw)
        assert _classify(raw) == base


@pytest.mark.parametrize("profile", PROFILES)
def test_foreign_skills_do_not_cause_rejection(profile):
    """sort_for_profile descarta lo ajeno al perfil antes del DFA."""
    assert _classify(CVS[profile] + ["Cobol", "Photoshop"])[profile] == ACCEPTED


def test_extra_skills_of_other_profiles_do_not_break_acceptance():
    raw = CVS["DATA_ANALYST"] + ["Git", "React", "Selenium"]
    assert _classify(raw)["DATA_ANALYST"] == ACCEPTED


def test_candidate_can_satisfy_several_profiles():
    raw = ["Python", "Pandas", "NumPy", "sklearn", "TensorFlow", "SQL", "Git",
           "Power BI", "Excel"]
    result = _classify(raw)
    assert result["MACHINE_LEARNING_ENGINEER"] == ACCEPTED
    assert result["DATA_ANALYST"] == ACCEPTED


@pytest.mark.parametrize("profile", PROFILES)
def test_incomplete_cv_is_rejected(profile):
    assert _classify(CVS[profile][:-1] if profile != "DATA_ANALYST" else ["SQL", "Python"])[profile] == REJECTED


def test_cv_matching_no_profile():
    assert accepted_profiles(normalize_qualifications(["Git"])) == []


def test_empty_and_none_are_rejected_everywhere():
    assert set(classify_candidate([]).values()) == {REJECTED}
    assert set(classify_candidate(None).values()) == {REJECTED}


def test_classify_profile_single_and_unknown():
    assert classify_profile(["GIT"], "QA_ENGINEER") == REJECTED
    with pytest.raises(KeyError):
        classify_profile(["GIT"], "CHEF")


def test_does_not_mutate_input():
    skills = ["GIT", "REACT"]
    classify_candidate(skills)
    assert skills == ["GIT", "REACT"]
