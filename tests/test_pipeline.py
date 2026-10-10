"""Tests for the ResumeLens pipeline orchestration module (src/pipeline.py)."""

from pathlib import Path

import pytest

from src.pipeline import (
    PipelineResult,
    extract_candidate_name,
    process_resume,
    run_pipeline,
)


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
    sample_path = Path("data/examples/sample_resume.txt")
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
