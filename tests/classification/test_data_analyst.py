"""Unit tests for the Data Analyst profile Deterministic Finite Automaton (DFA)."""

import itertools

from pyformlang.finite_automaton import State

from src.classification.data_analyst import (
    build_data_analyst_dfa,
    classify_data_analyst,
)


def test_valid_complete_with_excel():
    """Valid sequence containing all 5 categories (including optional Excel)."""
    skills = ["SQL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills) is True


def test_valid_without_excel():
    """Valid sequence with optional Excel omitted."""
    skills = ["SQL", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills) is True


def test_valid_with_postgresql():
    """Valid sequence using PostgreSQL as query language."""
    skills_with_excel = ["POSTGRESQL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_with_excel) is True

    skills_no_excel = ["POSTGRESQL", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_no_excel) is True


def test_valid_with_r():
    """Valid sequence using R as analysis language."""
    skills_with_excel = ["SQL", "EXCEL", "R", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_with_excel) is True

    skills_no_excel = ["SQL", "R", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_no_excel) is True


def test_valid_with_numpy_and_tableau():
    """Valid sequence combining PostgreSQL, Excel, R, NumPy, and Tableau."""
    skills = ["POSTGRESQL", "EXCEL", "R", "NUMPY", "TABLEAU"]
    assert classify_data_analyst(skills) is True

    skills_alt = ["MYSQL", "PYTHON", "NUMPY", "MATPLOTLIB"]
    assert classify_data_analyst(skills_alt) is True


def test_order_independence_explicit_cases():
    """The DFA must accept valid sets of skills regardless of the order in which they appear."""
    # Examples requested in the assignment audit:
    assert classify_data_analyst(["SQL", "PYTHON", "PANDAS", "POWER_BI"]) is True
    assert classify_data_analyst(["PYTHON", "SQL", "POWER_BI", "PANDAS"]) is True
    assert classify_data_analyst(["POWER_BI", "SQL", "PANDAS", "PYTHON"]) is True
    assert classify_data_analyst(["SQL", "POWER_BI", "PYTHON", "PANDAS"]) is True
    assert classify_data_analyst(["PYTHON", "PANDAS", "SQL", "TABLEAU"]) is True
    assert classify_data_analyst(["PYTHON", "SQL", "PANDAS", "POWER_BI"]) is True

    # Position of optional Excel does not alter acceptance:
    assert classify_data_analyst(["EXCEL", "SQL", "PYTHON", "PANDAS", "POWER_BI"]) is True
    assert classify_data_analyst(["SQL", "PYTHON", "EXCEL", "PANDAS", "POWER_BI"]) is True
    assert classify_data_analyst(["SQL", "PYTHON", "PANDAS", "POWER_BI", "EXCEL"]) is True
    assert classify_data_analyst(["POWER_BI", "EXCEL", "PANDAS", "SQL", "PYTHON"]) is True


def test_order_independence_all_permutations():
    """Verify that every permutation of the 4 mandatory categories is accepted."""
    base_skills = ["SQL", "PYTHON", "PANDAS", "POWER_BI"]
    permutations = list(itertools.permutations(base_skills))
    assert len(permutations) == 24

    for perm in permutations:
        assert classify_data_analyst(perm) is True, f"Failed for permutation: {perm}"


def test_multiple_skills_within_category():
    """Multiple skills within the same category are accepted via DFA self-loops."""
    skills_all_multi = [
        "MYSQL",
        "POSTGRESQL",
        "EXCEL",
        "PYTHON",
        "R",
        "PANDAS",
        "NUMPY",
        "POWER_BI",
        "TABLEAU",
    ]
    assert classify_data_analyst(skills_all_multi) is True

    # Interleaved order with multiple skills per category
    skills_interleaved = [
        "NUMPY",
        "SQL",
        "PYTHON",
        "POWER_BI",
        "PANDAS",
        "POSTGRESQL",
        "R",
        "TABLEAU",
    ]
    assert classify_data_analyst(skills_interleaved) is True


def test_duplicate_skills_handled():
    """Duplicate skills within a category are idempotent and do not break classification."""
    skills_with_duplicates = ["SQL", "SQL", "PYTHON", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_with_duplicates) is True

    # Repeated optional Excel:
    skills_repeat_excel = ["SQL", "EXCEL", "EXCEL", "PYTHON", "PANDAS", "POWER_BI"]
    assert classify_data_analyst(skills_repeat_excel) is True


def test_missing_query_language_rejected():
    """Sequence without mandatory QUERY_LANGUAGE is rejected."""
    assert classify_data_analyst(["EXCEL", "PYTHON", "PANDAS", "POWER_BI"]) is False
    assert classify_data_analyst(["PYTHON", "PANDAS", "POWER_BI"]) is False
    assert classify_data_analyst(["PYTHON", "NUMPY", "TABLEAU"]) is False


def test_missing_analysis_language_rejected():
    """Sequence without mandatory ANALYSIS_LANGUAGE is rejected."""
    assert classify_data_analyst(["SQL", "EXCEL", "PANDAS", "POWER_BI"]) is False
    assert classify_data_analyst(["SQL", "PANDAS", "POWER_BI"]) is False
    assert classify_data_analyst(["POSTGRESQL", "NUMPY", "TABLEAU"]) is False


def test_missing_data_processing_rejected():
    """Sequence without mandatory DATA_PROCESSING is rejected."""
    assert classify_data_analyst(["SQL", "EXCEL", "PYTHON", "POWER_BI"]) is False
    assert classify_data_analyst(["SQL", "PYTHON", "POWER_BI"]) is False
    assert classify_data_analyst(["MYSQL", "R", "MATPLOTLIB"]) is False


def test_missing_visualization_rejected():
    """Sequence without mandatory VISUALIZATION is rejected."""
    assert classify_data_analyst(["SQL", "EXCEL", "PYTHON", "PANDAS"]) is False
    assert classify_data_analyst(["SQL", "PYTHON", "PANDAS"]) is False
    assert classify_data_analyst(["POSTGRESQL", "R", "NUMPY"]) is False


def test_empty_list_rejected():
    """Empty list of qualifications is rejected."""
    assert classify_data_analyst([]) is False


def test_only_optional_excel_rejected():
    """Only Excel without mandatory categories is rejected."""
    assert classify_data_analyst(["EXCEL"]) is False
    assert classify_data_analyst(["EXCEL", "EXCEL"]) is False


def test_single_or_incomplete_subsets_rejected():
    """Incomplete subsets of categories are rejected."""
    assert classify_data_analyst(["SQL"]) is False
    assert classify_data_analyst(["SQL", "EXCEL"]) is False
    assert classify_data_analyst(["SQL", "PYTHON"]) is False
    assert classify_data_analyst(["SQL", "PANDAS"]) is False
    assert classify_data_analyst(["SQL", "POWER_BI"]) is False
    assert classify_data_analyst(["PYTHON", "PANDAS"]) is False
    assert classify_data_analyst(["PYTHON", "POWER_BI"]) is False
    assert classify_data_analyst(["PANDAS", "POWER_BI"]) is False


def test_foreign_tokens_rejected():
    """Tokens outside of the Data Analyst profile are rejected."""
    # Git is not a Data Analyst category token
    assert classify_data_analyst(["SQL", "EXCEL", "PYTHON", "PANDAS", "GIT"]) is False
    assert classify_data_analyst(["GIT", "SQL", "PYTHON", "PANDAS", "POWER_BI"]) is False

    # React is not a Data Analyst category token
    assert classify_data_analyst(["SQL", "REACT", "PYTHON", "PANDAS", "POWER_BI"]) is False
    assert classify_data_analyst(["DOCKER"]) is False


def test_dfa_formal_properties():
    """Verify formal properties of the 16-state order-independent DFA."""
    dfa = build_data_analyst_dfa()
    assert dfa.is_deterministic() is True
    assert len(dfa.start_states) == 1
    assert State("q_empty") in dfa.start_states
    assert len(dfa.final_states) == 1
    assert State("q_all_mandatory") in dfa.final_states
    assert len(dfa.states) == 16

    # Verify that the DFA is minimal
    minimized_dfa = dfa.minimize()
    assert len(minimized_dfa.states) == 16

