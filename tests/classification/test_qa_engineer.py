"""Unit tests for the QA Engineer profile Deterministic Finite Automaton (DFA)."""

from pyformlang.finite_automaton import State

from src.classification.qa_engineer import (
    build_qa_engineer_dfa,
    classify_qa_engineer,
)


def test_valid_complete_qa_engineer():
    """Valid candidate satisfying all 6 QA Engineer categories."""
    skills = ["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT"]
    assert classify_qa_engineer(skills) is True


def test_valid_alternatives():
    """Valid candidates using alternative technologies in each category."""
    skills_alt1 = ["JUNIT", "CYPRESS", "REST_ASSURED", "JAVA", "JIRA", "GIT"]
    assert classify_qa_engineer(skills_alt1) is True

    skills_alt2 = ["TESTNG", "PLAYWRIGHT", "POSTMAN", "JAVASCRIPT", "JIRA", "GIT"]
    assert classify_qa_engineer(skills_alt2) is True


def test_order_independence():
    """Valid skills accepted in arbitrary order."""
    skills = ["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT"]
    # Reverse order
    assert classify_qa_engineer(list(reversed(skills))) is True

    # Mixed order
    shuffled = ["JIRA", "PYTHON", "GIT", "SELENIUM", "PYTEST", "POSTMAN"]
    assert classify_qa_engineer(shuffled) is True


def test_multiple_skills_per_category():
    """Multiple skills within categories are accepted via DFA self-loops."""
    skills_multi = [
        "PYTEST",
        "JUNIT",
        "SELENIUM",
        "CYPRESS",
        "POSTMAN",
        "REST_ASSURED",
        "PYTHON",
        "JAVA",
        "JIRA",
        "GIT",
    ]
    assert classify_qa_engineer(skills_multi) is True


def test_duplicate_skills_handled():
    """Repeated skills are idempotent and do not break recognition."""
    skills = ["PYTEST", "PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT"]
    assert classify_qa_engineer(skills) is True


def test_missing_testing_rejected():
    """Missing mandatory TESTING category is rejected."""
    skills = ["SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT"]
    assert classify_qa_engineer(skills) is False


def test_missing_version_control_rejected():
    """Missing mandatory VERSION_CONTROL (GIT) is rejected."""
    skills = ["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA"]
    assert classify_qa_engineer(skills) is False


def test_missing_programming_rejected():
    """Missing mandatory PROGRAMMING category is rejected."""
    skills = ["PYTEST", "SELENIUM", "POSTMAN", "JIRA", "GIT"]
    assert classify_qa_engineer(skills) is False


def test_empty_list_rejected():
    """Empty list of skills is rejected."""
    assert classify_qa_engineer([]) is False


def test_foreign_skills_rejected():
    """Tokens outside of the QA Engineer profile cause rejection."""
    # SQL is from database profiles, not QA Engineer
    assert classify_qa_engineer(["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT", "SQL"]) is False
    # React is from frontend profile
    assert classify_qa_engineer(["PYTEST", "SELENIUM", "POSTMAN", "PYTHON", "JIRA", "GIT", "REACT"]) is False


def test_dfa_formal_properties():
    """Verify formal properties of the 64-state QA Engineer DFA."""
    dfa = build_qa_engineer_dfa()
    assert dfa.is_deterministic() is True
    assert len(dfa.start_states) == 1
    assert State("q_empty") in dfa.start_states
    assert len(dfa.final_states) == 1
    assert State("q_all_mandatory") in dfa.final_states
    assert len(dfa.states) == 64
