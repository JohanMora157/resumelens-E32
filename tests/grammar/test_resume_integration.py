"""Integration tests for ResumeLens Candidate Profile Language (CPL) grammar.

Tests real grammar compatibility (src/grammar/resume.tx) with:
- src.grammar.builder (build_dsl)
- src.grammar.validator (validate_dsl, is_valid_dsl)
- src.grammar.parser (parse_candidate_profile)
- src.grammar.renderer (render_html, render_markdown)

Validates complete and empty profiles, repeated experiences, multiple skills,
classification profiles, comments, syntax errors, and semantic validations
(0-60 experience years, duplicate skills, duplicate classification profiles).
"""

import pytest

from src.grammar.builder import build_dsl
from src.grammar.parser import parse_candidate_profile
from src.grammar.renderer import render_html, render_markdown
from src.grammar.validator import (
    GRAMMAR_PATH,
    DSLValidationError,
    _get_metamodel,
    is_valid_dsl,
    validate_dsl,
)


def test_real_grammar_file_exists_and_loads():
    """Verify resume.tx exists at default path and loads textX metamodel with processors."""
    assert GRAMMAR_PATH.is_file(), f"Grammar file not found: {GRAMMAR_PATH}"
    metamodel = _get_metamodel()
    assert metamodel is not None
    # Verify processors registered
    assert "Candidate" in metamodel._obj_processors
    assert "Experience" in metamodel._obj_processors
    assert "Skills" in metamodel._obj_processors
    assert "Classification" in metamodel._obj_processors


def test_complete_candidate_profile_end_to_end():
    """Build, validate, inspect, and render a complete candidate profile."""
    dsl = build_dsl(
        name="Ada Lovelace",
        email="ada@example.com",
        phone="+1-555-0100",
        experience=["3 years of algorithm design", "5 years of analytical computing"],
        education=["B.S. Mathematics", "M.S. Computing"],
        skills=["PYTHON", "JAVASCRIPT", "DOCKER", "POSTGRESQL", "GIT"],
        classification={
            "FULL_STACK_DEVELOPER": "ACCEPTED",
            "MACHINE_LEARNING_ENGINEER": "ACCEPTED",
            "QA_ENGINEER": "REJECTED",
            "DATA_ANALYST": "ACCEPTED",
        },
    )

    # Validate against the real grammar
    model = validate_dsl(dsl)
    assert is_valid_dsl(dsl) is True

    # Inspect model structure
    assert model.name == "Ada Lovelace"
    assert model.contact.email == "ada@example.com"
    assert model.contact.phone == "+1-555-0100"
    assert len(model.experiences) == 2
    assert model.experiences[0].years == 3
    assert model.experiences[1].years == 5
    assert model.education.entries == ["B.S. Mathematics", "M.S. Computing"]
    assert model.skills.names == ["PYTHON", "JAVASCRIPT", "DOCKER", "POSTGRESQL", "GIT"]
    assert len(model.classification.results) == 4

    results_map = {r.profile: r.status for r in model.classification.results}
    assert results_map["FULL_STACK_DEVELOPER"] == "ACCEPTED"
    assert results_map["MACHINE_LEARNING_ENGINEER"] == "ACCEPTED"
    assert results_map["QA_ENGINEER"] == "REJECTED"
    assert results_map["DATA_ANALYST"] == "ACCEPTED"

    # HTML rendering
    html = render_html(model)
    assert "<title>Ada Lovelace</title>" in html
    assert "ada@example.com" in html
    assert "+1-555-0100" in html
    assert "3 year(s)" in html
    assert "5 year(s)" in html
    assert "B.S. Mathematics" in html
    assert "<span class='chip'>PYTHON</span>" in html
    assert "Full Stack Developer" in html
    assert "class='ok'>ACCEPTED" in html
    assert "class='no'>REJECTED" in html

    # Markdown rendering
    md = render_markdown(model)
    assert "# Ada Lovelace" in md
    assert "- **Email:** ada@example.com" in md
    assert "- **Phone:** +1-555-0100" in md
    assert "- 3 year(s)" in md
    assert "- B.S. Mathematics" in md
    assert "`PYTHON`" in md
    assert "Full Stack Developer: **ACCEPTED**" in md
    assert "QA Engineer: **REJECTED**" in md


def test_empty_and_minimal_candidate_profile():
    """Validate empty candidate profile with no contact, experience, education, skills, or classification."""
    dsl = build_dsl("Minimal Candidate")

    model = validate_dsl(dsl)
    assert is_valid_dsl(dsl) is True

    assert model.name == "Minimal Candidate"
    assert model.contact.email is None
    assert model.contact.phone is None
    assert model.experiences == []
    assert model.education.entries == []
    assert model.skills.names == []
    assert model.classification.results == []

    # Rendering handles empty blocks gracefully without errors
    html = render_html(model)
    assert "Minimal Candidate" in html
    assert "<h2>Contact</h2>" not in html
    assert "<h2>Experience</h2>" not in html
    assert "<h2>Education</h2>" not in html
    assert "<h2>Skills</h2>" not in html
    assert "<h2>Profile classification</h2>" not in html

    md = render_markdown(model)
    assert "# Minimal Candidate" in md
    assert "## Experience" not in md
    assert "## Skills" not in md


def test_candidate_empty_name_defaults_to_unknown_candidate():
    """build_dsl with empty or whitespace name defaults to 'Unknown Candidate'."""
    dsl = build_dsl("")
    model = validate_dsl(dsl)
    assert model.name == "Unknown Candidate"


def test_repeated_experience_entries_with_descriptions():
    """Verify repeated experience entries, both with and without optional description."""
    dsl = (
        'candidate "Senior Architect" {\n'
        "  contact { }\n"
        '  experience { years: 2 description: "Junior engineer" }\n'
        '  experience { years: 4 description: "Senior engineer" }\n'
        '  experience { years: 6 description: "Principal architect" }\n'
        "  experience { years: 1 }\n"
        "  education { }\n"
        "  skills { GO, PYTHON }\n"
        "  classification { }\n"
        "}\n"
    )

    model = validate_dsl(dsl)
    assert len(model.experiences) == 4
    assert model.experiences[0].years == 2
    assert model.experiences[0].description == "Junior engineer"
    assert model.experiences[1].years == 4
    assert model.experiences[1].description == "Senior engineer"
    assert model.experiences[2].years == 6
    assert model.experiences[2].description == "Principal architect"
    assert model.experiences[3].years == 1
    assert model.experiences[3].description == ""

    # Verify rendering shows descriptions when present
    html = render_html(model)
    assert "2 year(s) &mdash; Junior engineer" in html
    assert "1 year(s)" in html

    md = render_markdown(model)
    assert "- 2 year(s) — Junior engineer" in md
    assert "- 1 year(s)" in md


def test_multiple_skills_validation_and_deduplication():
    """Multiple skills are accepted, preserved in order, and builder filters invalid identifiers."""
    skills_input = ["PYTHON", "JAVASCRIPT", "DOCKER", "AWS", "SQL", "POSTGRESQL", "GIT"]
    dsl = build_dsl("Skill Collector", skills=skills_input)

    model = validate_dsl(dsl)
    assert model.skills.names == skills_input

    # Builder ignores lowercase or invalid skill identifiers to avoid syntax violations
    dsl_dirty = build_dsl("Dirty Skills", skills=["python", "VALID_SKILL", "123invalid", "GIT"])
    model_dirty = validate_dsl(dsl_dirty)
    assert model_dirty.skills.names == ["VALID_SKILL", "GIT"]


def test_classification_results_combinations():
    """Classification accepts any subset of the 4 valid profiles with ACCEPTED or REJECTED status."""
    # Subset: single profile
    dsl_single = build_dsl("Single Profile", classification={"DATA_ANALYST": "ACCEPTED"})
    model_single = validate_dsl(dsl_single)
    assert len(model_single.classification.results) == 1
    assert model_single.classification.results[0].profile == "DATA_ANALYST"
    assert model_single.classification.results[0].status == "ACCEPTED"

    # All 4 profiles
    all_profiles = {
        "FULL_STACK_DEVELOPER": "REJECTED",
        "MACHINE_LEARNING_ENGINEER": "ACCEPTED",
        "QA_ENGINEER": "ACCEPTED",
        "DATA_ANALYST": "REJECTED",
    }
    dsl_all = build_dsl("All Profiles", classification=all_profiles)
    model_all = validate_dsl(dsl_all)
    assert len(model_all.classification.results) == 4


def test_comments_in_dsl():
    """Single-line and multi-line comments are supported and ignored by the grammar."""
    dsl = (
        '// Top-level comment: Candidate profile\n'
        'candidate "Alan Turing" {\n'
        "  /* Contact information block */\n"
        "  contact { email: alan@bletchley.uk }\n"
        "  // Experience block\n"
        "  experience { years: 12 }\n"
        "  education { \"Cambridge University\" }\n"
        "  skills { MATHEMATICS, CRYPTOGRAPHY } // Cryptanalysis\n"
        "  /* Classification block\n"
        "     Multiple lines\n"
        "  */\n"
        "  classification {\n"
        "    MACHINE_LEARNING_ENGINEER: ACCEPTED\n"
        "  }\n"
        "}\n"
    )

    model = validate_dsl(dsl)
    assert model.name == "Alan Turing"
    assert model.contact.email == "alan@bletchley.uk"
    assert model.experiences[0].years == 12
    assert model.skills.names == ["MATHEMATICS", "CRYPTOGRAPHY"]


def test_parse_candidate_profile_dict_integration():
    """parse_candidate_profile integrates dictionary input with real grammar validation."""
    data = {
        "name": "Grace Hopper",
        "email": "grace@navy.mil",
        "phone": "+1-555-0100",
        "experience": ["10 years of systems programming"],
        "education": ["Ph.D. Yale University"],
        "skills": ["COBOL", "FORTRAN", "COMPILERS"],
        "classification": {"FULL_STACK_DEVELOPER": "ACCEPTED"},
    }

    model = parse_candidate_profile(data)
    assert model.name == "Grace Hopper"
    assert model.contact.email == "grace@navy.mil"
    assert model.experiences[0].years == 10
    assert "COBOL" in model.skills.names


@pytest.mark.parametrize(
    "invalid_dsl,error_description",
    [
        (
            'candidate "Incomplete" { }',
            "Missing mandatory blocks (contact, education, skills, classification)",
        ),
        (
            'candidate "Missing Contact" { education {} skills {} classification {} }',
            "Omission of mandatory contact block",
        ),
        (
            'candidate Ada { contact {} education {} skills {} classification {} }',
            "Candidate name must be a quoted STRING",
        ),
        (
            'candidate { contact {} education {} skills {} classification {} }',
            "Missing candidate name before opening brace",
        ),
        (
            'candidate "Unclosed" { contact {}',
            "Unclosed candidate brace",
        ),
        (
            'candidate "Bad Email" { contact { email: not-an-email } education {} skills {} classification {} }',
            "Malformed email address",
        ),
        (
            'candidate "Bad Phone" { contact { phone: 12 } education {} skills {} classification {} }',
            "Phone number too short",
        ),
        (
            'candidate "Bad Skill" { contact {} education {} skills { python } classification {} }',
            "Skill names must be uppercase [A-Z][A-Z0-9_]*",
        ),
        (
            'candidate "Bad Profile" { contact {} education {} skills {} classification { UNKNOWN_PROFILE: ACCEPTED } }',
            "Unknown profile name not in ProfileName enum",
        ),
        (
            'candidate "Bad Status" { contact {} education {} skills {} classification { DATA_ANALYST: PENDING } }',
            "Status must be ACCEPTED or REJECTED",
        ),
    ],
)
def test_syntax_errors_rejected(invalid_dsl, error_description):
    """Syntactically invalid DSL programs raise DSLValidationError with kind='syntax'."""
    with pytest.raises(DSLValidationError) as exc:
        validate_dsl(invalid_dsl)
    assert exc.value.kind == "syntax", f"Expected syntax error for: {error_description}"
    assert is_valid_dsl(invalid_dsl) is False


@pytest.mark.parametrize("invalid_years", [-1, -10, 61, 75, 100])
def test_semantic_experience_years_outside_0_60_rejected(invalid_years):
    """Semantic validation rejects experience years outside [0, 60]."""
    dsl = (
        'candidate "Time Traveler" {\n'
        "  contact { }\n"
        f"  experience {{ years: {invalid_years} }}\n"
        "  education { }\n"
        "  skills { PYTHON }\n"
        "  classification { }\n"
        "}\n"
    )

    with pytest.raises(DSLValidationError) as exc:
        validate_dsl(dsl)
    assert exc.value.kind == "semantic"
    assert "fuera de rango (0-60)" in str(exc.value)
    assert is_valid_dsl(dsl) is False


@pytest.mark.parametrize("valid_years", [0, 1, 15, 30, 45, 60])
def test_semantic_experience_years_boundary_values_accepted(valid_years):
    """Semantic validation accepts experience years at boundaries 0 and 60, and within range."""
    dsl = (
        'candidate "Boundary Candidate" {\n'
        "  contact { }\n"
        f"  experience {{ years: {valid_years} }}\n"
        "  education { }\n"
        "  skills { PYTHON }\n"
        "  classification { }\n"
        "}\n"
    )

    model = validate_dsl(dsl)
    assert model.experiences[0].years == valid_years
    assert is_valid_dsl(dsl) is True


@pytest.mark.parametrize("empty_name", ['""', '"   "', '" \t \n "'])
def test_semantic_empty_candidate_name_rejected(empty_name):
    """Semantic validation rejects empty or whitespace-only candidate name in raw DSL."""
    dsl = (
        f"candidate {empty_name} {{\n"
        "  contact { }\n"
        "  education { }\n"
        "  skills { }\n"
        "  classification { }\n"
        "}\n"
    )

    with pytest.raises(DSLValidationError) as exc:
        validate_dsl(dsl)
    assert exc.value.kind == "semantic"
    assert "no puede estar vacío" in str(exc.value)
    assert is_valid_dsl(dsl) is False


def test_semantic_duplicate_skills_rejected():
    """Semantic validation rejects duplicate skill names in raw DSL."""
    dsl = (
        'candidate "Duplicate Skills" {\n'
        "  contact { }\n"
        "  education { }\n"
        "  skills { PYTHON, SQL, PYTHON }\n"
        "  classification { }\n"
        "}\n"
    )

    with pytest.raises(DSLValidationError) as exc:
        validate_dsl(dsl)
    assert exc.value.kind == "semantic"
    assert "Skill repetida: PYTHON" in str(exc.value)
    assert is_valid_dsl(dsl) is False


def test_semantic_duplicate_classification_profiles_rejected():
    """Semantic validation rejects duplicate profile results in raw DSL."""
    dsl = (
        'candidate "Duplicate Profiles" {\n'
        "  contact { }\n"
        "  education { }\n"
        "  skills { }\n"
        "  classification {\n"
        "    FULL_STACK_DEVELOPER: ACCEPTED\n"
        "    FULL_STACK_DEVELOPER: REJECTED\n"
        "  }\n"
        "}\n"
    )

    with pytest.raises(DSLValidationError) as exc:
        validate_dsl(dsl)
    assert exc.value.kind == "semantic"
    assert "Perfil repetido en la clasificación: FULL_STACK_DEVELOPER" in str(exc.value)
    assert is_valid_dsl(dsl) is False
