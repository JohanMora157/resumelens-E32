"""Tests de los DFA por perfil: objeto formal, aceptación, rechazo y orden."""

import itertools
import random

import pytest

from src.classification.data_analyst import classify_data_analyst
from src.classification.full_stack_developer import build_full_stack_dfa, classify_full_stack
from src.classification.machine_learning_engineer import build_ml_engineer_dfa, classify_ml_engineer
from src.classification.profile_dfa import accepts, build_profile_dfa, mandatory_categories
from src.classification.profiles import (
    DATA_ANALYST, FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER, PROFILES, QA_ENGINEER,
)
from src.classification.qa_engineer import build_qa_engineer_dfa, classify_qa_engineer

OPTIONAL = {
    "FULL_STACK_DEVELOPER": {"API"},
    "MACHINE_LEARNING_ENGINEER": set(),
    "QA_ENGINEER": set(),
    "DATA_ANALYST": {"SPREADSHEET"},
}
CLASSIFY = {
    "FULL_STACK_DEVELOPER": classify_full_stack,
    "MACHINE_LEARNING_ENGINEER": classify_ml_engineer,
    "QA_ENGINEER": classify_qa_engineer,
    "DATA_ANALYST": classify_data_analyst,
}


def _one_per_mandatory(name):
    p = PROFILES[name]
    return [p["categories"][c][0] for c in mandatory_categories(p, OPTIONAL[name])]


# ---------- el objeto formal ----------

@pytest.mark.parametrize("name", PROFILES)
def test_dfa_is_deterministic_with_2_to_the_k_states(name):
    p = PROFILES[name]
    dfa = build_profile_dfa(p, OPTIONAL[name])
    k = len(mandatory_categories(p, OPTIONAL[name]))
    assert dfa.is_deterministic()
    assert len(dfa.states) == 2 ** k
    assert len(dfa.final_states) == 1


@pytest.mark.parametrize("name", PROFILES)
def test_alphabet_is_all_profile_tokens(name):
    p = PROFILES[name]
    dfa = build_profile_dfa(p, OPTIONAL[name])
    expected = {t for toks in p["categories"].values() for t in toks}
    assert {str(s) for s in dfa.symbols} == expected


def test_state_counts():
    assert len(build_full_stack_dfa().states) == 2 ** 5
    assert len(build_ml_engineer_dfa().states) == 2 ** 6
    assert len(build_qa_engineer_dfa().states) == 2 ** 6


def test_unknown_optional_category_raises():
    with pytest.raises(ValueError):
        build_profile_dfa(QA_ENGINEER, optional={"NOPE"})


# ---------- aceptación ----------

@pytest.mark.parametrize("name", PROFILES)
def test_one_token_per_mandatory_category_is_accepted(name):
    assert CLASSIFY[name](_one_per_mandatory(name))


@pytest.mark.parametrize("name", PROFILES)
def test_any_permutation_is_accepted(name):
    skills = _one_per_mandatory(name)
    for seed in range(15):
        shuffled = skills[:]
        random.Random(seed).shuffle(shuffled)
        assert CLASSIFY[name](shuffled)


@pytest.mark.parametrize("name", PROFILES)
def test_every_alternative_of_each_category_is_accepted(name):
    p = PROFILES[name]
    mand = mandatory_categories(p, OPTIONAL[name])
    base = _one_per_mandatory(name)
    for i, cat in enumerate(mand):
        for token in p["categories"][cat]:
            seq = base[:]
            seq[i] = token
            assert CLASSIFY[name](seq), (name, token)


@pytest.mark.parametrize("name", PROFILES)
def test_repeated_and_extra_tokens_of_same_category_are_accepted(name):
    skills = _one_per_mandatory(name)
    assert CLASSIFY[name](skills + skills)
    assert CLASSIFY[name](skills + [skills[0]])


def test_ml_engineer_accepts_pandas_and_numpy_together():
    seq = ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]
    assert classify_ml_engineer(seq)


def test_pdf_example_ml_engineer():
    assert classify_ml_engineer(["PYTHON", "PANDAS", "SCIKIT_LEARN", "TENSORFLOW", "POSTGRESQL", "GIT"])


def test_pdf_example_full_stack_without_rest_api():
    """Wednesday Addams (PDF) no menciona REST: API es opcional y debe ser ACCEPTED."""
    assert classify_full_stack(["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])


def test_optional_category_is_accepted_when_present():
    assert classify_full_stack(["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API", "GIT"])
    assert classify_data_analyst(["SQL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"])


# ---------- rechazo ----------

@pytest.mark.parametrize("name", PROFILES)
def test_missing_any_mandatory_category_is_rejected(name):
    skills = _one_per_mandatory(name)
    for i in range(len(skills)):
        assert not CLASSIFY[name](skills[:i] + skills[i + 1:]), (name, i)


@pytest.mark.parametrize("name", PROFILES)
def test_empty_is_rejected(name):
    assert not CLASSIFY[name]([])


@pytest.mark.parametrize("name", PROFILES)
def test_foreign_token_is_rejected_by_the_dfa(name):
    assert not CLASSIFY[name](_one_per_mandatory(name) + ["COBOL"])


@pytest.mark.parametrize("name", PROFILES)
def test_only_optional_tokens_is_rejected(name):
    p = PROFILES[name]
    opts = [t for c in OPTIONAL[name] for t in p["categories"][c]]
    if opts:
        assert not CLASSIFY[name](opts)


def test_tokens_of_another_profile_do_not_satisfy():
    assert not classify_qa_engineer(["PANDAS", "NUMPY", "TABLEAU", "SQL"])


# ---------- consistencia con el DFA de Data Analyst (el original del equipo) ----------

def test_generic_builder_matches_original_data_analyst_dfa():
    generic = build_profile_dfa(DATA_ANALYST, {"SPREADSHEET"})
    tokens = [t for ts in DATA_ANALYST["categories"].values() for t in ts]
    rng = random.Random(7)
    for _ in range(400):
        seq = [rng.choice(tokens) for _ in range(rng.randint(0, 7))]
        assert accepts(generic, seq) == classify_data_analyst(seq), seq


def test_exhaustive_data_analyst_sequences_up_to_length_four():
    generic = build_profile_dfa(DATA_ANALYST, {"SPREADSHEET"})
    tokens = ["SQL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"]
    for n in range(0, 5):
        for seq in itertools.product(tokens, repeat=n):
            assert accepts(generic, seq) == classify_data_analyst(seq)