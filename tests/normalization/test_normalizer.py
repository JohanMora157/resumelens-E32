"""Tests de normalizer.py: clean_token, normalize_skill, normalize y normalize_qualifications."""

import json

import pytest

from src.normalization.normalizer import (
    clean_token, normalize, normalize_qualifications, normalize_skill,
)
from src.normalization.transducers import ALIASES_PATH


# ---------- casos positivos: alias del PDF y propios ----------

@pytest.mark.parametrize("raw,expected", [
    ("JS", "JAVASCRIPT"), ("Javascript", "JAVASCRIPT"), ("js", "JAVASCRIPT"), ("JAVASCRIPT", "JAVASCRIPT"),
    ("React.js", "REACT"), ("ReactJS", "REACT"), ("react", "REACT"), ("REACT JS", "REACT"),
    ("NodeJS", "NODE_JS"), ("Node.js", "NODE_JS"), ("Node", "NODE_JS"), ("node js", "NODE_JS"),
    ("Postgres", "POSTGRESQL"), ("PostgreSQL", "POSTGRESQL"), ("postgre sql", "POSTGRESQL"),
    ("sklearn", "SCIKIT_LEARN"), ("scikit learn", "SCIKIT_LEARN"), ("Scikit-learn", "SCIKIT_LEARN"),
    ("Tensor Flow", "TENSORFLOW"), ("TensorFlow", "TENSORFLOW"),
    ("Py Torch", "PYTORCH"), ("PyTorch", "PYTORCH"),
    ("pandas", "PANDAS"), ("NumPy", "NUMPY"), ("Git", "GIT"), ("SQL", "SQL"),
    ("Power BI", "POWER_BI"), ("PowerBI", "POWER_BI"), ("Spring Boot", "SPRING_BOOT"),
    ("REST APIs", "REST_API"), ("RESTful", "REST_API"),
    ("Cypress.io", "CYPRESS"), ("JUnit5", "JUNIT"), ("RestAssured", "REST_ASSURED"),
])
def test_equivalent_forms_map_to_canonical(raw, expected):
    assert normalize_skill(raw) == expected


def test_case_insensitive_for_every_variant():
    for raw in ("javascript", "JAVASCRIPT", "JaVaScRiPt"):
        assert normalize_skill(raw) == "JAVASCRIPT"


# ---------- idempotencia: el token canónico se reconoce a sí mismo ----------

def test_every_canonical_token_normalizes_to_itself():
    data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    for family in data.values():
        for canonical in family:
            assert normalize_skill(canonical) == canonical, canonical


# ---------- casos negativos: deben dar None ----------

@pytest.mark.parametrize("raw", [
    "Cobol", "Photoshop",                       # fuera del vocabulario
    "Reactt", "Node.jss", "Java Scrip", "Re act",   # casi-alias
    "Nod", "React.j",                           # prefijos de un alias
    "React.js, Node", "JS JS",                  # dos skills pegadas
    "123", "😀", "Pythön",                      # basura / caracteres ajenos
    "", "   ", "...", "-", "()",                # vacío o solo ruido
    "a" * 500,                                  # entrada larga
])
def test_non_vocabulary_input_returns_none(raw):
    assert normalize_skill(raw) is None


# ---------- clean_token ----------

@pytest.mark.parametrize("raw,expected", [
    ("Git.", "GIT"), ("Node  JS", "NODE_JS"), ("(Python)", "PYTHON"),
    ("- React.js", "REACT"), ("\u2022 JS", "JAVASCRIPT"), ("  Postgres;", "POSTGRESQL"),
    ("Scikit\u2011learn,", "SCIKIT_LEARN"), ('"Git"', "GIT"), ("\tJS\n", "JAVASCRIPT"),
])
def test_noisy_tokens_are_normalized(raw, expected):
    assert normalize_skill(raw) == expected


def test_clean_token_keeps_inner_dots():
    assert clean_token("Node.js.") == "Node.js"


def test_clean_token_collapses_spaces():
    assert clean_token("Spring    Boot") == "Spring Boot"


def test_clean_token_only_noise_gives_empty_string():
    assert clean_token("...") == ""
    assert clean_token("   ") == ""


def test_clean_token_does_not_decide_equivalence():
    """La limpieza no normaliza: eso es trabajo exclusivo del FST."""
    assert clean_token("JS.") == "JS"
    assert clean_token("sklearn") == "sklearn"


# ---------- normalize() ----------

def test_normalize_empty_list():
    assert normalize([]) == ([], [])


def test_normalize_only_unknown():
    assert normalize(["Cobol", "Fortran"]) == ([], ["Cobol", "Fortran"])


def test_normalize_deduplicates_equivalent_forms():
    known, unknown = normalize(["JS", "js", "Javascript"])
    assert known == ["JAVASCRIPT"] and unknown == []


def test_normalize_unknown_not_repeated():
    assert normalize(["Cobol", "Cobol"])[1] == ["Cobol"]


def test_normalize_keeps_order_of_first_appearance():
    known, _ = normalize(["Git", "JS", "Postgres", "git"])
    assert known == ["GIT", "JAVASCRIPT", "POSTGRESQL"]


def test_normalize_mixed_known_and_unknown():
    known, unknown = normalize(["JS", "Cobol", "Git"])
    assert known == ["JAVASCRIPT", "GIT"] and unknown == ["Cobol"]


def test_pdf_reference_examples():
    wednesday, _ = normalize(["JS", "React.js", "NodeJS", "Postgres", "Git"])
    assert wednesday == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    mary, _ = normalize(["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"])
    assert mary == ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]


# ---------- contrato con el pipeline ----------

def test_normalize_qualifications_returns_plain_list_of_str():
    result = normalize_qualifications(["JS", "Postgres", "Git.", "Cobol"])
    assert isinstance(result, list)
    assert all(isinstance(x, str) for x in result)
    assert result == ["JAVASCRIPT", "POSTGRESQL", "GIT"]


def test_normalize_qualifications_empty():
    assert normalize_qualifications([]) == []