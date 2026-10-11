"""Tests de integración: texto del CV -> resultado completo del pipeline."""

from pathlib import Path

import pytest

from src.pipeline import (
    PipelineResult,
    extract_candidate_name,
    process_resume,
    run_pipeline,
)

WEDNESDAY = """Wednesday Addams
Email: wednesday.addams@example.com | Phone: +1-555-0199
3 years of experience developing web applications.
Education:
Bachelor's degree in Computer Science
Technical Skills:
JS, React.js, NodeJS, Postgres, Git."""

MARY_JANE = """Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."""

QA = """Peter Parker
Technical Skills:
pytest, Selenium, Postman, Python, Jira, Git"""

DATA = """Gwen Stacy
Technical Skills:
SQL, Excel, Python, pandas, Power BI"""

PROFILES = ["FULL_STACK_DEVELOPER", "MACHINE_LEARNING_ENGINEER", "QA_ENGINEER", "DATA_ANALYST"]


def _accepted(result):
    return [p for p, s in result.classification.items() if s == "ACCEPTED"]


def test_wednesday_addams_end_to_end():
    r = run_pipeline(WEDNESDAY)
    assert r.error is None
    assert r.name == "Wednesday Addams"
    assert r.canonical_skills == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert _accepted(r) == ["FULL_STACK_DEVELOPER"]
    assert r.model.contact.email == "wednesday.addams@example.com"
    assert "Wednesday Addams" in r.html and "# Wednesday Addams" in r.markdown


def test_mary_jane_watson_end_to_end():
    r = run_pipeline(MARY_JANE)
    assert r.error is None
    assert r.canonical_skills == ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]
    assert _accepted(r) == ["MACHINE_LEARNING_ENGINEER"]


@pytest.mark.parametrize("cv,profile", [(QA, "QA_ENGINEER"), (DATA, "DATA_ANALYST")])
def test_own_profiles_end_to_end(cv, profile):
    r = run_pipeline(cv)
    assert r.error is None and profile in _accepted(r)


def test_result_always_lists_the_four_profiles():
    assert list(run_pipeline(WEDNESDAY).classification) == PROFILES
    assert list(run_pipeline("").classification) == PROFILES


def test_sorted_skills_are_exposed_per_profile():
    r = run_pipeline(WEDNESDAY)
    assert r.sorted_by_profile["FULL_STACK_DEVELOPER"] == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert r.sorted_by_profile["DATA_ANALYST"] == ["POSTGRESQL"]   # Postgres también es QUERY_LANGUAGE
    assert r.sorted_by_profile["QA_ENGINEER"] == ["JAVASCRIPT", "GIT"]


def test_unknown_skills_are_reported_not_fatal():
    r = run_pipeline(WEDNESDAY.replace("Git.", "Git, Cobol"))
    assert r.unknown_skills == ["Cobol"] and r.error is None
    assert _accepted(r) == ["FULL_STACK_DEVELOPER"]


def test_cv_that_matches_no_profile_still_produces_a_valid_profile_sheet():
    r = run_pipeline("Tony Stark\nTechnical Skills:\nGit")
    assert _accepted(r) == [] and r.error is None and r.html


@pytest.mark.parametrize("text", ["", "   \n  ", "texto sin ninguna información útil", "!!! ??? ###"])
def test_empty_or_noisy_input_does_not_crash(text):
    r = run_pipeline(text)
    assert r.error is None
    assert set(r.classification.values()) == {"REJECTED"}
    assert r.name == "Unknown Candidate"


def test_noisy_formatting_is_cleaned_before_the_fst():
    cv = "Ana Torres\nTechnical Skills:\n  - JS ,  React.js ; (NodeJS) | Postgres , Git. "
    assert _accepted(run_pipeline(cv)) == ["FULL_STACK_DEVELOPER"]


def test_skill_order_in_the_cv_does_not_change_the_classification():
    a = run_pipeline(WEDNESDAY).classification
    b = run_pipeline(WEDNESDAY.replace("JS, React.js, NodeJS, Postgres, Git.", "Git, Postgres, NodeJS, React.js, JS")).classification
    assert a == b


def test_spanish_resume():
    cv = ("Johan Mora\nEmail: johan.mora@example.com | Teléfono: +57 300 123 4567\n"
          "Profesional con 3 años de experiencia en desarrollo de software.\n"
          "Educación:\nIngeniería de Sistemas\nHabilidades Técnicas:\nJS, React.js, NodeJS, Postgres, Git.")
    r = run_pipeline(cv)
    assert r.error is None and _accepted(r) == ["FULL_STACK_DEVELOPER"]
    assert r.model.experiences[0].years == 3

def test_extract_candidate_name_heuristics():
    """Verifies candidate name heuristic extraction across various resume formats."""
    # Standard clean name on first line
    cv1 = "Ada Lovelace\nada@example.com | 555-0100\nTechnical Skills:\nPython"
    assert extract_candidate_name(cv1) == "Ada Lovelace"

    # Name preceded by markdown heading formatting
    cv2 = "# Alan Turing\nTechnical Skills:\nPython"
    assert extract_candidate_name(cv2) == "Alan Turing"

    # First lines are headers or contact details
    cv3 = """
    Contact:
    john.doe@example.com
    +1 (555) 123-4567

    John Doe
    Technical Skills:
    Git, SQL
    """
    assert extract_candidate_name(cv3) == "John Doe"

    # Empty and whitespace inputs
    assert extract_candidate_name("") == "Unknown Candidate"
    assert extract_candidate_name("   \n\t  ") == "Unknown Candidate"


def test_run_pipeline_sample_resume():
    """Verifies end-to-end execution with the sample resume (Wednesday Addams)."""
    sample_path = Path(__file__).resolve().parents[2] / "data" / "examples" / "sample_resume.txt"
    assert sample_path.exists(), "Sample resume file must exist"

    sample_text = sample_path.read_text(encoding="utf-8")
    result = run_pipeline(sample_text)

    # 1. Structure
    assert isinstance(result, PipelineResult)
    assert result.name == "Wednesday Addams"

    # 2. Extraction
    contact = result.extracted["contact"]
    assert contact["email"] == "wednesday.addams@example.com"
    assert contact["phone"] == "+1-555-0199"
    assert "3 years of experience" in result.extracted["experience"]
    assert any("Computer Science" in e for e in result.extracted["education"])
    assert result.extracted["technical_skills"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]

    # 3. Normalization
    expected_canonical = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.canonical_skills == expected_canonical
    assert result.unknown_skills == []

    # 4. Canonical order per profile
    fs_sorted = result.sorted_by_profile["FULL_STACK_DEVELOPER"]
    assert fs_sorted == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]

    # 5. DFA Classification
    assert result.classification["FULL_STACK_DEVELOPER"] == "ACCEPTED"
    assert result.classification["MACHINE_LEARNING_ENGINEER"] == "REJECTED"

    # 6. DSL Generation
    assert 'candidate "Wednesday Addams" {' in result.dsl_text
    assert "FULL_STACK_DEVELOPER: ACCEPTED" in result.dsl_text
    assert "MACHINE_LEARNING_ENGINEER: REJECTED" in result.dsl_text


def test_run_pipeline_ml_candidate():
    """Verifies pipeline processing for a Machine Learning Engineer candidate."""
    cv_text = """Nikola Tesla
    Email: nikola.tesla@inventor.org | Phone: +1-555-0144
    5 years of experience in machine learning systems.
    Education:
    Master's degree in Artificial Intelligence
    Technical Skills:
    Python, Pandas, Scikit-learn, PyTorch, SQL, Git.
    """
    result = run_pipeline(cv_text)

    assert result.name == "Nikola Tesla"
    assert "PYTHON" in result.canonical_skills
    assert "SCIKIT_LEARN" in result.canonical_skills
    assert "PYTORCH" in result.canonical_skills
    assert result.classification["MACHINE_LEARNING_ENGINEER"] == "ACCEPTED"
    assert result.classification["FULL_STACK_DEVELOPER"] == "REJECTED"


def test_run_pipeline_empty_resume():
    """Verifies that running the pipeline on empty text yields safe defaults without exceptions."""
    result = run_pipeline("")

    assert isinstance(result, PipelineResult)
    assert result.name == "Unknown Candidate"
    assert result.extracted["contact"]["email"] is None
    assert result.extracted["contact"]["phone"] is None
    assert result.extracted["technical_skills"] == []
    assert result.canonical_skills == []
    assert result.unknown_skills == []
    assert result.classification["FULL_STACK_DEVELOPER"] == "REJECTED"
    assert result.classification["MACHINE_LEARNING_ENGINEER"] == "REJECTED"
    assert result.classification["QA_ENGINEER"] == "REJECTED"
    assert result.classification["DATA_ANALYST"] == "REJECTED"
    assert 'candidate "Unknown Candidate" {' in result.dsl_text


def test_process_resume_compatibility_alias():
    """Verifies that process_resume returns identical results to run_pipeline."""
    text = "Dev Candidate\nSkills:\nPython, Git"
    res1 = run_pipeline(text)
    res2 = process_resume(text)

    assert res1.name == res2.name
    assert res1.canonical_skills == res2.canonical_skills
    assert res1.classification == res2.classification
    assert res1.dsl_text == res2.dsl_text
