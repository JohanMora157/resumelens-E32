"""Tests de la etapa 2: FST de normalización y sorter."""

import pytest

from src.classification.profiles import (
    DATA_ANALYST, FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER, PROFILES, QA_ENGINEER,
)
from src.normalization.normalizer import (
    clean_token, normalize, normalize_qualifications, normalize_skill,
)
from src.normalization.sorter import sort_for_profile
from src.normalization.transducers import build_fst, load_fsts


@pytest.mark.parametrize("raw,expected", [
    ("JS", "JAVASCRIPT"), ("Javascript", "JAVASCRIPT"), ("js", "JAVASCRIPT"),
    ("React.js", "REACT"), ("ReactJS", "REACT"), ("react", "REACT"),
    ("NodeJS", "NODE_JS"), ("Node.js", "NODE_JS"), ("Node", "NODE_JS"),
    ("Postgres", "POSTGRESQL"), ("PostgreSQL", "POSTGRESQL"),
    ("sklearn", "SCIKIT_LEARN"), ("scikit learn", "SCIKIT_LEARN"), ("Scikit-learn", "SCIKIT_LEARN"),
    ("Tensor Flow", "TENSORFLOW"), ("TensorFlow", "TENSORFLOW"),
    ("Py Torch", "PYTORCH"), ("PyTorch", "PYTORCH"),
    ("pandas", "PANDAS"), ("Git", "GIT"), ("  Git  ", "GIT"),
])
def test_normalize_skill(raw, expected):
    assert normalize_skill(raw) == expected


def test_unknown_and_empty():
    assert normalize_skill("Cobol") is None
    assert normalize_skill("") is None
    assert normalize_skill("Nod") is None      # prefijo de un alias, no alias completo


def test_normalize_list_dedup_and_unknown():
    known, unknown = normalize(["JS", "Javascript", "Cobol", "Git"])
    assert known == ["JAVASCRIPT", "GIT"]
    assert unknown == ["Cobol"]


def test_pdf_example_sorted_full_stack():
    known, _ = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    assert sort_for_profile(known, FULL_STACK_DEVELOPER) == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]


def test_order_of_input_does_not_matter():
    a = sort_for_profile(["GIT", "REACT", "JAVASCRIPT"], FULL_STACK_DEVELOPER)
    b = sort_for_profile(["JAVASCRIPT", "GIT", "REACT"], FULL_STACK_DEVELOPER)
    assert a == b


def test_sorter_discards_foreign_tokens():
    assert sort_for_profile(["GIT", "PYTHON", "PANDAS"], DATA_ANALYST) == ["PYTHON", "PANDAS"]


def test_same_token_other_category_ml():
    assert sort_for_profile(["GIT", "SQL", "PYTHON"], MACHINE_LEARNING_ENGINEER) == ["PYTHON", "SQL", "GIT"]


def test_fst_is_a_real_seven_tuple():
    for fst in load_fsts().values():
        assert fst.states and fst.input_symbols and fst.output_symbols
        assert len(fst.start_states) == 1 and fst.final_states


def test_ambiguous_alias_raises():
    with pytest.raises(ValueError):
        build_fst({"A": ["x"], "B": ["X"]})


def test_profiles_vocabulary_is_produced_by_fst():
    """Todo token de un perfil debe poder salir del FST (vocabulario compartido)."""
    import json
    from src.normalization.transducers import ALIASES_PATH
    produced = {c for fam in json.loads(ALIASES_PATH.read_text()).values() for c in fam}
    for name, p in PROFILES.items():
        for cat, tokens in p["categories"].items():
            for t in tokens:
                assert t in produced, f"{t} ({name}/{cat}) no lo emite ningún FST"


def test_no_token_in_two_categories_within_profile():
    for name, p in PROFILES.items():
        flat = [t for ts in p["categories"].values() for t in ts]
        assert len(flat) == len(set(flat)), name
        assert set(p["canonical_order"]) == set(p["categories"]), name


# ---------- clean_token: ruido de formato antes del FST ----------

@pytest.mark.parametrize("raw,expected", [
    ("Git.", "GIT"), ("Node  JS", "NODE_JS"), ("(Python)", "PYTHON"),
    ("- React.js", "REACT"), ("\u2022 JS", "JAVASCRIPT"), ("  Postgres;", "POSTGRESQL"),
    ("Scikit\u2011learn,", "SCIKIT_LEARN"),
])
def test_noisy_tokens_are_normalized(raw, expected):
    assert normalize_skill(raw) == expected


def test_clean_token_keeps_inner_dots():
    assert clean_token("Node.js.") == "Node.js"


def test_clean_token_only_noise_gives_none():
    assert normalize_skill("...") is None
    assert normalize_skill("   ") is None


def test_clean_token_does_not_decide_equivalence():
    """La limpieza no normaliza: eso es trabajo exclusivo del FST."""
    assert clean_token("JS.") == "JS"


def test_normalize_qualifications_returns_plain_list():
    assert normalize_qualifications(["JS", "Postgres", "Git."]) == ["JAVASCRIPT", "POSTGRESQL", "GIT"]