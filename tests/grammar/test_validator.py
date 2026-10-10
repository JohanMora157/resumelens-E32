"""Unit tests for Stage 4 DSL Validator (src/grammar/validator.py) and Parser (src/grammar/parser.py).

Verifies semantic rules, error structure, lazy grammar loading behavior,
and end-to-end validation with textX.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest
from textx.exceptions import TextXSemanticError

from src.grammar.parser import parse_candidate_profile
from src.grammar.validator import (
    DSLValidationError,
    _check_candidate,
    _check_classification,
    _check_experience,
    _check_skills,
    is_valid_dsl,
    validate_dsl,
)

SAMPLE_GRAMMAR = """
Candidate:
    'candidate' name=STRING '{'
        contact=Contact?
        experiences*=Experience
        education=Education?
        skills=Skills?
        classification=Classification?
    '}'
;

Contact:
    'contact' '{'
        ('email:' email=/[^\\s}]+/)?
        ('phone:' phone=/[^\\s}][^}\\n]*/)?
    '}'
;

Experience:
    'experience' '{'
        'years:' years=INT
        ('description:' description=STRING)?
    '}'
;

Education:
    'education' '{'
        entries*=STRING[',']
    '}'
;

Skills:
    'skills' '{'
        names*=ID[',']
    '}'
;

Classification:
    'classification' '{'
        results*=ProfileResult
    '}'
;

ProfileResult:
    profile=ID ':' status=ID
;
"""


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


def test_experience_none_or_missing_rejected():
    """7. Experience with None or missing years is rejected."""
    with pytest.raises(TextXSemanticError) as exc:
        _check_experience(SimpleNamespace(years=None))
    assert "fuera de rango" in str(exc.value)


def test_duplicate_skills_rejected():
    """8. Duplicate skill identifiers are rejected by _check_skills."""
    duplicate_skills = SimpleNamespace(names=["PYTHON", "SQL", "PYTHON"])
    with pytest.raises(TextXSemanticError) as exc:
        _check_skills(duplicate_skills)
    assert "Skill repetida: PYTHON" in str(exc.value)


def test_unique_skills_pass():
    """9. Unique skill identifiers pass their semantic check."""
    unique_skills = SimpleNamespace(names=["PYTHON", "SQL", "POSTGRESQL", "PANDAS", "DOCKER"])
    _check_skills(unique_skills)

    # Empty skill list also passes
    _check_skills(SimpleNamespace(names=[]))


def test_duplicate_classification_profiles_rejected():
    """10. Duplicate profile results in classification are rejected."""
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
    """11. Unique classification profiles pass their semantic check."""
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


def test_missing_grammar_raises_configuration_error(tmp_path: Path):
    """12. Calling validate_dsl when resume.tx is absent raises DSLValidationError with kind='configuration'."""
    missing_grammar = tmp_path / "non_existent_resume.tx"
    with pytest.raises(DSLValidationError) as exc:
        validate_dsl('candidate "Ada Lovelace" { }', grammar_path=missing_grammar)
    assert exc.value.kind == "configuration"
    assert "El archivo de gramática no existe" in str(exc.value)


def test_is_valid_dsl_propagates_missing_grammar_configuration_error(tmp_path: Path):
    """13. is_valid_dsl() does not silently return False when the grammar is absent."""
    missing_grammar = tmp_path / "non_existent_resume.tx"
    with pytest.raises(DSLValidationError) as exc:
        is_valid_dsl('candidate "Ada Lovelace" { }', grammar_path=missing_grammar)
    assert exc.value.kind == "configuration"


def test_parse_candidate_profile_type_error():
    """14. parse_candidate_profile raises TypeError when given unsupported input types."""
    with pytest.raises(TypeError) as exc:
        parse_candidate_profile(12345)
    assert "Tipo de dato no soportado" in str(exc.value)

    with pytest.raises(TypeError):
        parse_candidate_profile(["not", "a", "dict"])


def test_parse_candidate_profile_propagates_config_error(tmp_path: Path):
    """15. parse_candidate_profile propagates configuration error when grammar is missing."""
    missing_grammar = tmp_path / "non_existent_resume.tx"
    with pytest.raises(DSLValidationError) as exc:
        parse_candidate_profile(
            {
                "name": "Alan Turing",
                "skills": ["PYTHON", "SQL"],
            },
            grammar_path=missing_grammar,
        )
    assert exc.value.kind == "configuration"


def test_end_to_end_validation_with_grammar_fixture(tmp_path: Path):
    """16. Verifies complete end-to-end metamodel loading, parsing, and semantic validation."""
    grammar_file = tmp_path / "resume.tx"
    grammar_file.write_text(SAMPLE_GRAMMAR, encoding="utf-8")

    valid_dsl = (
        'candidate "Grace Hopper" {\n'
        "  contact { email: grace@navy.mil phone: +1-555-0100 }\n"
        "  experience { years: 10 }\n"
        '  education { "Ph.D. Yale" }\n'
        "  skills { COBOL, FORTRAN }\n"
        "  classification {\n"
        "    FULL_STACK_DEVELOPER: ACCEPTED\n"
        "    QA_ENGINEER: ACCEPTED\n"
        "  }\n"
        "}\n"
    )

    # Valid parsing
    model = validate_dsl(valid_dsl, grammar_path=grammar_file)
    assert model.name == "Grace Hopper"
    assert model.contact.email == "grace@navy.mil"
    assert model.experiences[0].years == 10
    assert "COBOL" in model.skills.names
    assert is_valid_dsl(valid_dsl, grammar_path=grammar_file) is True

    # Dictionary input via parse_candidate_profile
    model_from_dict = parse_candidate_profile(
        {
            "name": "Margaret Hamilton",
            "contact": {"email": "margaret@mit.edu", "phone": "1234567"},
            "experience": ["5 years of experience"],
            "education": ["B.A. in Mathematics"],
            "skills": ["PYTHON", "GIT"],
            "classification": {"FULL_STACK_DEVELOPER": "ACCEPTED"},
        },
        grammar_path=grammar_file,
    )
    assert model_from_dict.name == "Margaret Hamilton"

    # Syntax violation
    syntax_broken = 'candidate "Broken" { invalid syntax here }'
    with pytest.raises(DSLValidationError) as exc_syntax:
        validate_dsl(syntax_broken, grammar_path=grammar_file)
    assert exc_syntax.value.kind == "syntax"
    assert is_valid_dsl(syntax_broken, grammar_path=grammar_file) is False

    # Semantic violation: years > 60
    semantic_invalid_years = (
        'candidate "Methuselah" {\n'
        "  experience { years: 90 }\n"
        "}\n"
    )
    with pytest.raises(DSLValidationError) as exc_years:
        validate_dsl(semantic_invalid_years, grammar_path=grammar_file)
    assert exc_years.value.kind == "semantic"
    assert "fuera de rango" in str(exc_years.value)
    assert is_valid_dsl(semantic_invalid_years, grammar_path=grammar_file) is False

    # Semantic violation: duplicate skill
    semantic_duplicate_skills = (
        'candidate "Duplicate Skill Candidate" {\n'
        "  skills { PYTHON, SQL, PYTHON }\n"
        "}\n"
    )
    with pytest.raises(DSLValidationError) as exc_skills:
        validate_dsl(semantic_duplicate_skills, grammar_path=grammar_file)
    assert exc_skills.value.kind == "semantic"
    assert "Skill repetida" in str(exc_skills.value)
