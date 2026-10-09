"""Unit tests for Stage 4 DSL Builder (src/grammar/builder.py)."""

import pytest

from src.grammar.builder import PROFILE_ORDER, _quote, build_dsl, parse_years


def test_complete_candidate_dsl():
    """1. Generating a complete candidate DSL with all sections populated."""
    dsl = build_dsl(
        name="Grace Hopper",
        email="grace.hopper@navy.mil",
        phone="+1 (555) 019-2834",
        experience=["10 years in compiler design", "five years of systems engineering"],
        education=["Ph.D. in Mathematics, Yale University", "B.A. in Mathematics, Vassar College"],
        skills=["COBOL", "FORTRAN", "COMPILER"],
        classification={
            "FULL_STACK_DEVELOPER": "ACCEPTED",
            "QA_ENGINEER": "ACCEPTED",
            "DATA_ANALYST": "REJECTED",
        },
    )

    expected = (
        'candidate "Grace Hopper" {\n'
        "  contact { email: grace.hopper@navy.mil  phone: +1 (555) 019-2834 }\n"
        "  experience { years: 10 }\n"
        "  experience { years: 5 }\n"
        '  education { "Ph.D. in Mathematics, Yale University", "B.A. in Mathematics, Vassar College" }\n'
        "  skills { COBOL, FORTRAN, COMPILER }\n"
        "  classification {\n"
        "    FULL_STACK_DEVELOPER: ACCEPTED\n"
        "    QA_ENGINEER: ACCEPTED\n"
        "    DATA_ANALYST: REJECTED\n"
        "  }\n"
        "}\n"
    )
    assert dsl == expected


def test_candidate_without_optional_fields():
    """2. Generating a candidate with minimal / omitted optional fields."""
    dsl = build_dsl(name="Alan Turing")

    expected = (
        'candidate "Alan Turing" {\n'
        "  contact { }\n"
        "  education { }\n"
        "  skills { }\n"
        "  classification {\n"
        "  }\n"
        "}\n"
    )
    assert dsl == expected

    # Fallback when name is empty or None
    dsl_empty_name = build_dsl(name="")
    assert dsl_empty_name.startswith('candidate "Unknown Candidate" {\n')

    dsl_none_name = build_dsl(name=None)
    assert dsl_none_name.startswith('candidate "Unknown Candidate" {\n')


def test_valid_and_invalid_email_handling():
    """3. Valid email is included, invalid or malformed email is discarded."""
    # Valid emails
    dsl_valid = build_dsl(name="Test User", email="user.name+tag@sub.domain.co")
    assert "email: user.name+tag@sub.domain.co" in dsl_valid

    # Stripping spaces around valid email
    dsl_stripped = build_dsl(name="Test User", email="   valid@example.org   ")
    assert "email: valid@example.org" in dsl_stripped

    # Invalid emails should be omitted
    for bad_email in ["notanemail", "user@domain", "@nodomain.com", "spaces in@email.com", ""]:
        dsl_bad = build_dsl(name="Test User", email=bad_email)
        assert "email:" not in dsl_bad
        assert "contact { }" in dsl_bad


def test_valid_and_invalid_phone_handling():
    """4. Valid phone is included, invalid or malformed phone is discarded."""
    # Valid phones
    for good_phone in ["+1-555-123-4567", "(555) 234-5678", "+57 300 123 4567", "1234567"]:
        dsl_valid = build_dsl(name="Test User", phone=good_phone)
        assert f"phone: {good_phone}" in dsl_valid

    # Invalid phones should be omitted
    for bad_phone in ["abc", "12", "call-me", ""]:
        dsl_bad = build_dsl(name="Test User", phone=bad_phone)
        assert "phone:" not in dsl_bad
        assert "contact { }" in dsl_bad


def test_experience_expressed_as_numbers():
    """5. Experience expressed as numeric digits is extracted properly."""
    assert parse_years("3 years of experience") == 3
    assert parse_years("5+ años de experiencia en desarrollo") == 5
    assert parse_years("Over 12 years in IT") == 12
    assert parse_years("1 year") == 1
    assert parse_years("No duration mentioned") is None

    dsl = build_dsl(name="Dev", experience=["4 years with Python", "2 years with AWS", "internship"])
    assert "experience { years: 4 }" in dsl
    assert "experience { years: 2 }" in dsl
    # "internship" has no numbers, should not produce an experience block
    assert dsl.count("experience {") == 2


def test_experience_expressed_as_english_number_words():
    """6. Experience expressed as English number words is parsed correctly."""
    word_tests = [
        ("one year of experience", 1),
        ("two years developing frontend", 2),
        ("three years in data science", 3),
        ("four years building APIs", 4),
        ("five years in QA automation", 5),
        ("six years of engineering", 6),
        ("seven years leading teams", 7),
        ("eight years in cloud architecture", 8),
        ("nine years of research", 9),
        ("ten years in industry", 10),
    ]
    for text, expected in word_tests:
        assert parse_years(text) == expected
        assert parse_years(text.upper()) == expected

    # Digits take priority if both present
    assert parse_years("two years and 5 months") == 5


def test_education_deduplication():
    """7. Duplicate education entries are deduplicated while preserving order."""
    education = [
        "B.S. in Computer Science",
        "M.S. in Software Engineering",
        "B.S. in Computer Science",
        "Ph.D. in Artificial Intelligence",
        "M.S. in Software Engineering",
    ]
    dsl = build_dsl(name="Academic Candidate", education=education)
    expected_edu = (
        'education { "B.S. in Computer Science", '
        '"M.S. in Software Engineering", '
        '"Ph.D. in Artificial Intelligence" }'
    )
    assert expected_edu in dsl


def test_skill_deduplication():
    """8. Duplicate skills are deduplicated while preserving order."""
    skills = ["PYTHON", "SQL", "PYTHON", "REACT", "SQL", "DOCKER", "REACT"]
    dsl = build_dsl(name="Polyglot Dev", skills=skills)
    assert "skills { PYTHON, SQL, REACT, DOCKER }" in dsl


def test_rejection_of_incorrectly_formatted_canonical_skills():
    """9. Non-canonical skills not matching SKILL_RE are omitted."""
    mixed_skills = [
        "PYTHON",          # valid
        "python",          # invalid: lowercase
        "Node.js",         # invalid: punctuation dot
        "C++",             # invalid: plus symbols
        "JAVASCRIPT",      # valid
        "123_INVALID",     # invalid: starts with number
        "KUBERNETES",      # valid
        "",                # invalid: empty
        "DATA SCIENCE",    # invalid: contains space
        "SPRING_BOOT",     # valid
    ]
    dsl = build_dsl(name="Candidate", skills=mixed_skills)
    assert "skills { PYTHON, JAVASCRIPT, KUBERNETES, SPRING_BOOT }" in dsl


def test_classification_output_profile_order():
    """10. Classification entries are output in canonical PROFILE_ORDER."""
    classification = {
        "DATA_ANALYST": "ACCEPTED",
        "FULL_STACK_DEVELOPER": "REJECTED",
        "QA_ENGINEER": "ACCEPTED",
        "MACHINE_LEARNING_ENGINEER": "REJECTED",
    }
    dsl = build_dsl(name="Multi Profile", classification=classification)

    # Extract classification block lines
    lines = [line.strip() for line in dsl.splitlines() if line.strip().startswith(tuple(PROFILE_ORDER))]
    assert lines == [
        "FULL_STACK_DEVELOPER: REJECTED",
        "MACHINE_LEARNING_ENGINEER: REJECTED",
        "QA_ENGINEER: ACCEPTED",
        "DATA_ANALYST: ACCEPTED",
    ]

    # Partial classification outputs only provided profiles in relative order
    partial = {"QA_ENGINEER": "ACCEPTED", "FULL_STACK_DEVELOPER": "ACCEPTED"}
    dsl_partial = build_dsl(name="Partial", classification=partial)
    partial_lines = [line.strip() for line in dsl_partial.splitlines() if line.strip().startswith(tuple(PROFILE_ORDER))]
    assert partial_lines == [
        "FULL_STACK_DEVELOPER: ACCEPTED",
        "QA_ENGINEER: ACCEPTED",
    ]


def test_correct_escaping_and_quoting():
    """11. Correct escaping of quotes, stripping of backslashes, and normalization of spaces."""
    assert _quote('Ada "Lovelace" Byron') == '"Ada \\"Lovelace\\" Byron"'
    assert _quote('Path\\To\\Folder') == '"PathToFolder"'
    assert _quote("Multiple   spaces \n and\ttabs") == '"Multiple spaces and tabs"'

    dsl = build_dsl(
        name='Dr. Martin "Bob" Vance',
        education=['Diploma in "Computer Systems", MIT'],
    )
    assert 'candidate "Dr. Martin \\"Bob\\" Vance" {' in dsl
    assert 'education { "Diploma in \\"Computer Systems\\", MIT" }' in dsl


def test_consistent_output_formatting_and_no_unnecessary_blank_lines():
    """12. Output format consistency: no double newlines and ends with single newline."""
    dsl = build_dsl(
        name="Clean Candidate",
        email="clean@example.com",
        phone="555-123456",
        experience=["1 year"],
        education=["B.S."],
        skills=["PYTHON"],
        classification={"FULL_STACK_DEVELOPER": "ACCEPTED"},
    )
    assert not dsl.endswith("\n\n")
    assert dsl.endswith("\n")
    assert "\n\n" not in dsl

    # Check that contact with only email or only phone has correct single spaces inside braces
    dsl_email_only = build_dsl(name="Candidate", email="a@b.com")
    assert "  contact { email: a@b.com }\n" in dsl_email_only

    dsl_phone_only = build_dsl(name="Candidate", phone="1234567")
    assert "  contact { phone: 1234567 }\n" in dsl_phone_only
