"""Tests de sorter.py y de la consistencia de los perfiles con el vocabulario del FST."""

import json
import random

import pytest

from src.classification.profiles import (
    DATA_ANALYST, FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER, PROFILES, QA_ENGINEER,
)
from src.normalization.normalizer import normalize
from src.normalization.sorter import sort_for_profile
from src.normalization.transducers import ALIASES_PATH


# ---------- caso de oro por perfil: texto del CV -> FST -> orden canónico ----------

GOLDEN = [
    (FULL_STACK_DEVELOPER,
     ["Git", "NodeJS", "JS", "Postgres", "React.js", "REST APIs"],
     ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API", "GIT"]),
    (MACHINE_LEARNING_ENGINEER,
     ["Git", "SQL", "TensorFlow", "sklearn", "NumPy", "Pandas", "Python"],
     ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]),
    (QA_ENGINEER,
     ["Git", "Jira", "Python", "Postman", "Selenium", "pytest"],
     ["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT"]),
    (DATA_ANALYST,
     ["Power BI", "Python", "Excel", "SQL", "pandas"],
     ["SQL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"]),
]


@pytest.mark.parametrize("profile,raw,expected", GOLDEN)
def test_golden_case_per_profile(profile, raw, expected):
    known, _ = normalize(raw)
    assert sort_for_profile(known, profile) == expected


def test_pdf_example_full_stack():
    known, _ = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    assert sort_for_profile(known, FULL_STACK_DEVELOPER) == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]


# ---------- el orden de entrada no importa ----------

@pytest.mark.parametrize("profile,raw,expected", GOLDEN)
def test_input_order_does_not_change_output(profile, raw, expected):
    for seed in range(10):
        shuffled = raw[:]
        random.Random(seed).shuffle(shuffled)
        known, _ = normalize(shuffled)
        assert sort_for_profile(known, profile) == expected


# ---------- bordes ----------

@pytest.mark.parametrize("profile", PROFILES.values())
def test_empty_input_gives_empty_output(profile):
    assert sort_for_profile([], profile) == []


@pytest.mark.parametrize("profile", PROFILES.values())
def test_only_foreign_tokens_gives_empty_output(profile):
    assert sort_for_profile(["COBOL", "PHOTOSHOP"], profile) == []


def test_sorter_discards_foreign_tokens():
    assert sort_for_profile(["GIT", "PYTHON", "PANDAS"], DATA_ANALYST) == ["PYTHON", "PANDAS"]


def test_repeated_tokens_are_not_duplicated():
    assert sort_for_profile(["GIT", "GIT", "REACT", "REACT"], FULL_STACK_DEVELOPER) == ["REACT", "GIT"]


def test_two_options_of_same_category_keep_declared_order():
    assert sort_for_profile(["NUMPY", "PANDAS"], MACHINE_LEARNING_ENGINEER) == ["PANDAS", "NUMPY"]


def test_same_token_changes_position_between_profiles():
    skills = ["GIT", "SQL", "PYTHON"]
    assert sort_for_profile(skills, MACHINE_LEARNING_ENGINEER) == ["PYTHON", "SQL", "GIT"]
    assert sort_for_profile(skills, DATA_ANALYST) == ["SQL", "PYTHON"]


def test_sorter_does_not_modify_its_input():
    skills = ["GIT", "REACT"]
    sort_for_profile(skills, FULL_STACK_DEVELOPER)
    assert skills == ["GIT", "REACT"]


# ---------- consistencia de los perfiles con el vocabulario del FST ----------

def test_profiles_vocabulary_is_produced_by_fst():
    produced = {c for fam in json.loads(ALIASES_PATH.read_text(encoding="utf-8")).values() for c in fam}
    for name, p in PROFILES.items():
        for cat, tokens in p["categories"].items():
            for t in tokens:
                assert t in produced, f"{t} ({name}/{cat}) no lo emite ningún FST"


def test_no_token_in_two_categories_within_profile():
    for name, p in PROFILES.items():
        flat = [t for ts in p["categories"].values() for t in ts]
        assert len(flat) == len(set(flat)), name


def test_canonical_order_matches_categories():
    for name, p in PROFILES.items():
        assert set(p["canonical_order"]) == set(p["categories"]), name
        assert len(p["canonical_order"]) == len(set(p["canonical_order"])), name


def test_every_category_has_at_least_one_option():
    for name, p in PROFILES.items():
        assert all(p["categories"][c] for c in p["canonical_order"]), name


def test_four_profiles_defined():
    assert set(PROFILES) == {
        "FULL_STACK_DEVELOPER", "MACHINE_LEARNING_ENGINEER", "QA_ENGINEER", "DATA_ANALYST"}