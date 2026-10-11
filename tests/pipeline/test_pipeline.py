"""Tests de integración: texto del CV -> resultado completo del pipeline."""

import pytest

from src.pipeline import run_pipeline

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