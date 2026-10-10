"""Unit tests for Stage 4 DSL Validator (src/grammar/validator.py).

Verifies semantic rules, error structure, and lazy grammar loading behavior
without requiring the missing resume.tx file.
"""

from types import SimpleNamespace

import pytest
from textx.exceptions import TextXSemanticError

from src.grammar.validator import (
    DSLValidationError,
    _check_candidate,
    _check_classification,
    _check_experience,
    _check_skills,
    is_valid_dsl,
    validate_dsl,
)


def test_validator_imports_successfully():
    """1. validator.py can be imported without error even when resume.tx is absent."""
    import src.grammar.validator as validator_module

    assert hasattr(validator_module, "DSLValidationError")
    assert hasattr(validator_module, "validate_dsl")
    assert hasattr(validator_module, "is_valid_dsl")


def test_dsl_validation_error_attributes():
    """2. DSLValidationError stores message, kind, line, and col accurately."""
    err_syntax = DSLValidationError("Syntax problem", kind="syntax")
    assert str(err_syntax) == "Syntax problem"
    assert err_syntax.kind == "syntax"
    assert err_syntax.line is None
    assert err_syntax.col is None

    err_semantic = DSLValidationError("Semantic rule broken", kind="semantic", line=12, col=5)
    assert err_semantic.kind == "semantic"
    assert err_semantic.line == 12
    assert err_semantic.col == 5

    err_config = DSLValidationError("Missing grammar", kind="configuration")
    assert err_config.kind == "configuration"


def test_candidate_empty_or_whitespace_name_rejected():
    """3. Candidate with an empty or whitespace-only name is rejected by _check_candidate."""
    # Empty string
    with pytest.raises(TextXSemanticError) as exc_empty:
        _check_candidate(SimpleNamespace(name=""))
    assert "no puede estar vacío" in str(exc_empty.value)

    # Whitespace only
    with pytest.raises(TextXSemanticError) as exc_ws:
        _check_candidate(SimpleNamespace(name="   \t\n  "))
    assert "no puede estar vacío" in str(exc_ws.value)

    # Valid name passes without error
    _check_candidate(SimpleNamespace(name="Grace Hopper"))


def test_experience_below_zero_rejected():
    """4. Experience with years < 0 is rejected by _check_experience."""
    with pytest.raises(TextXSemanticError) as exc:
        _check_experience(SimpleNamespace(years=-1))
    assert "fuera de rango" in str(exc.value)

    with pytest.raises(TextXSemanticError):
        _check_experience(SimpleNamespace(years=-15))


def test_experience_above_max_rejected():
    """5. Experience with years > 60 is rejected by _check_experience."""
    with pytest.raises(TextXSemanticError) as exc:
        _check_experience(SimpleNamespace(years=61))
    assert "fuera de rango" in str(exc.value)

    with pytest.raises(TextXSemanticError):
        _check_experience(SimpleNamespace(years=100))


def test_experience_within_valid_range_passes():
    """6. Experience with 0 <= years <= 60 passes its semantic check."""
    # Boundary and intermediate values
    _check_experience(SimpleNamespace(years=0))
    _check_experience(SimpleNamespace(years=1))
    _check_experience(SimpleNamespace(years=5))
    _check_experience(SimpleNamespace(years=30))
    _check_experience(SimpleNamespace(years=60))


def test_duplicate_skills_rejected():
    """7. Duplicate skill identifiers are rejected by _check_skills."""
    duplicate_skills = SimpleNamespace(names=["PYTHON", "SQL", "PYTHON"])
    with pytest.raises(TextXSemanticError) as exc:
        _check_skills(duplicate_skills)
    assert "Skill repetida: PYTHON" in str(exc.value)


def test_unique_skills_pass():
    """8. Unique skill identifiers pass their semantic check."""
    unique_skills = SimpleNamespace(names=["PYTHON", "SQL", "POSTGRESQL", "PANDAS", "DOCKER"])
    _check_skills(unique_skills)

    # Empty skill list also passes
    _check_skills(SimpleNamespace(names=[]))


def test_duplicate_classification_profiles_rejected():
    """9. Duplicate profile results in classification are rejected."""
    duplicate_profiles = SimpleNamespace(
        results=[
            SimpleNamespace(profile="FULL_STACK_DEVELOPER", status="ACCEPTED"),
            SimpleNamespace(profile="QA_ENGINEER", status="ACCEPTED"),
            SimpleNamespace(profile="FULL_STACK_DEVELOPER", status="REJECTED"),
        ]
    )
    with pytest.raises(TextXSemanticError) as exc:
        _check_classification(duplicate_profiles)
    assert "Perfil repetido en la clasificación: FULL_STACK_DEVELOPER" in str(exc.value)


def test_unique_classification_profiles_pass():
    """10. Unique classification profiles pass their semantic check."""
    unique_profiles = SimpleNamespace(
        results=[
            SimpleNamespace(profile="FULL_STACK_DEVELOPER", status="ACCEPTED"),
            SimpleNamespace(profile="MACHINE_LEARNING_ENGINEER", status="REJECTED"),
            SimpleNamespace(profile="QA_ENGINEER", status="ACCEPTED"),
            SimpleNamespace(profile="DATA_ANALYST", status="ACCEPTED"),
        ]
    )
    _check_classification(unique_profiles)

    # Empty classification results also passes
    _check_classification(SimpleNamespace(results=[]))


def test_missing_grammar_raises_configuration_error():
    """11. Calling validate_dsl when resume.tx is absent raises DSLValidationError with kind='configuration'."""
    with pytest.raises(DSLValidationError) as exc:
        validate_dsl('candidate "Ada Lovelace" { }')
    assert exc.value.kind == "configuration"
    assert "El archivo de gramática no existe" in str(exc.value)


def test_is_valid_dsl_propagates_missing_grammar_configuration_error():
    """12. is_valid_dsl() does not silently return False when the grammar is absent."""
    with pytest.raises(DSLValidationError) as exc:
        is_valid_dsl('candidate "Ada Lovelace" { }')
    assert exc.value.kind == "configuration"
