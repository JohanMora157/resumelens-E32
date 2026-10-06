"""Unit tests for the regular expression extraction module (Stage 1).

Verifies extraction of:
1. Email addresses
2. Phone numbers
3. Explicit professional experience mentions
4. Technical skills section headers
5. Multiple skills across various delimiters (, ; | \\n)
6. Academic degrees and fields of study
7. Full resume with multiple categories simultaneously
8. Resume with missing categories without errors
9. Strict preservation of original token casing and representation
10. Absence of semantic normalization (Regex is not FST)
11. Assignment reference examples (Wednesday Addams and Mary Jane Watson)
"""

from pathlib import Path

from src.extraction.regex_extractor import (
    extract_contact_info,
    extract_education,
    extract_experience,
    extract_resume_information,
    extract_technical_skills,
)


def test_extract_email_single_and_multiple():
    """Test extraction of single and multiple email addresses."""
    text_single = "Contact me at candidate.developer@domain.com for opportunities."
    result_single = extract_resume_information(text_single)
    assert result_single["contact"]["email"] == "candidate.developer@domain.com"
    assert "candidate.developer@domain.com" in result_single["contact"]["emails"]

    text_multiple = "Primary: lead@tech.org | Backup: personal_2026@mail.edu"
    result_multiple = extract_resume_information(text_multiple)
    assert result_multiple["contact"]["email"] == "lead@tech.org"
    assert len(result_multiple["contact"]["emails"]) == 2
    assert "personal_2026@mail.edu" in result_multiple["contact"]["emails"]


def test_extract_phone_formats():
    """Test extraction of phone numbers across common formatting conventions."""
    formats = [
        ("Phone: +1-555-123-4567", "+1-555-123-4567"),
        ("Tel: (555) 234-5678", "(555) 234-5678"),
        ("Mobile: +57 300 123 4567", "+57 300 123 4567"),
        ("Direct: 555-345-6789", "555-345-6789"),
    ]
    for text, expected_number in formats:
        contact = extract_contact_info(text)
        assert contact["phone"] == expected_number
        assert expected_number in contact["phones"]


def test_extract_experience():
    """Test extraction of explicit professional experience mentions."""
    test_cases = [
        ("Candidate with 3 years of experience in web systems.", "3 years of experience"),
        ("Possesses 2 years experience developing models.", "2 years experience"),
        ("Engineer with 5+ years of experience in cloud architectures.", "5+ years of experience"),
        ("Cuenta con 3 años de experiencia en desarrollo.", "3 años de experiencia"),
        ("Over 4 years of professional experience in software.", "4 years of professional experience"),
    ]
    for text, expected in test_cases:
        res = extract_experience(text)
        assert expected in res, f"Expected '{expected}' to be in {res}"


def test_extract_technical_skills_section():
    """Test detection of skills sections with various header styles."""
    sample_skills = "JS, React.js, NodeJS"

    headers = [
        f"Technical Skills:\n{sample_skills}",
        f"Skills:\n{sample_skills}",
        f"Technical Skills\n{sample_skills}",
        f"Technologies:\n{sample_skills}",
        f"Programming Languages:\n{sample_skills}",
    ]

    for text in headers:
        skills = extract_technical_skills(text)
        assert skills == ["JS", "React.js", "NodeJS"], f"Failed for header: {text}"


def test_extract_multiple_skills_in_same_section():
    """Test extraction of multiple skills within a section using different delimiters."""
    # Comma delimited
    text_comma = "Technical Skills: Python, Django, PostgreSQL, Git"
    assert extract_technical_skills(text_comma) == ["Python", "Django", "PostgreSQL", "Git"]

    # Semicolon delimited
    text_semi = "Technologies: Python; Django; PostgreSQL; Git"
    assert extract_technical_skills(text_semi) == ["Python", "Django", "PostgreSQL", "Git"]

    # Pipe delimited
    text_pipe = "Skills: Python | Django | PostgreSQL | Git"
    assert extract_technical_skills(text_pipe) == ["Python", "Django", "PostgreSQL", "Git"]

    # Newline and bullet delimited
    text_bullets = """Technical Skills:
    - Python
    - Django
    - PostgreSQL
    - Git
    """
    assert extract_technical_skills(text_bullets) == ["Python", "Django", "PostgreSQL", "Git"]


def test_extract_academic_education():
    """Test extraction of recognized academic degrees and fields of study."""
    text = """
    Education:
    Bachelor's degree in Computer Science
    Also studied Software Engineering and completed a Master's degree.
    """
    education = extract_education(text)
    assert "Bachelor's degree" in education
    assert "Computer Science" in education
    assert "Software Engineering" in education
    assert "Master's degree" in education

    text_es = "Formación: Grado en Ingeniería de Sistemas"
    education_es = extract_education(text_es)
    assert "Ingeniería de Sistemas" in education_es


def test_resume_with_all_categories():
    """Test processing of a complete resume containing all categories."""
    cv = """
    John Doe
    Email: john.doe@example.com | Phone: +1-555-0144
    Software Developer with 4 years of experience building scalable systems.

    Education:
    Bachelor's degree in Software Engineering

    Technical Skills:
    Python, FastAPI, PostgreSQL, Docker, Git.
    """
    result = extract_resume_information(cv)

    assert result["contact"]["email"] == "john.doe@example.com"
    assert result["contact"]["phone"] == "+1-555-0144"
    assert "4 years of experience" in result["experience"]
    assert "Bachelor's degree" in result["education"]
    assert "Software Engineering" in result["education"]
    assert result["technical_skills"] == ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"]


def test_resume_with_missing_categories_does_not_fail():
    """Test that missing categories do not raise errors and return clean defaults."""
    # Resume with only technical skills
    cv_only_skills = "Technical Skills: Python, SQL"
    res1 = extract_resume_information(cv_only_skills)
    assert res1["contact"]["email"] is None
    assert res1["contact"]["phone"] is None
    assert res1["contact"]["emails"] == []
    assert res1["contact"]["phones"] == []
    assert res1["experience"] == []
    assert res1["education"] == []
    assert res1["technical_skills"] == ["Python", "SQL"]

    # Empty text
    res_empty = extract_resume_information("")
    assert res_empty["contact"]["email"] is None
    assert res_empty["contact"]["emails"] == []
    assert res_empty["experience"] == []
    assert res_empty["education"] == []
    assert res_empty["technical_skills"] == []

    # Descriptive text with no structured categories
    res_desc = extract_resume_information("Just some general text without qualifications or contacts.")
    assert res_desc["contact"]["email"] is None
    assert res_desc["experience"] == []
    assert res_desc["education"] == []
    assert res_desc["technical_skills"] == []


def test_preserves_original_text_representation():
    """Test that extracted values preserve original text casing and punctuation."""
    cv = """
    Technical Skills:
    JS, React.js, NodeJS, Postgres, Scikit-learn, TensorFlow, Git.
    """
    result = extract_resume_information(cv)
    skills = result["technical_skills"]

    assert "JS" in skills
    assert "React.js" in skills
    assert "NodeJS" in skills
    assert "Postgres" in skills
    assert "Scikit-learn" in skills
    assert "TensorFlow" in skills
    assert "Git" in skills


def test_regex_does_not_normalize_equivalences():
    """Verify that Regex stage does NOT perform FST normalizations."""
    cv = """
    Technical Skills:
    JS, React.js, NodeJS, Postgres, sklearn, Tensor Flow.
    """
    result = extract_resume_information(cv)
    skills = result["technical_skills"]

    # Canonical forms belonging to FST stage must not appear
    assert "JAVASCRIPT" not in skills
    assert "REACT" not in skills
    assert "NODE_JS" not in skills
    assert "POSTGRESQL" not in skills
    assert "SCIKIT_LEARN" not in skills
    assert "TENSORFLOW" not in skills

    # Tokens must remain exactly as written
    assert "JS" in skills
    assert "React.js" in skills
    assert "NodeJS" in skills
    assert "Postgres" in skills
    assert "sklearn" in skills
    assert "Tensor Flow" in skills


def test_consigna_example_wednesday_addams():
    """Test the reference example for Wednesday Addams from the assignment."""
    cv = """Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git."""

    result = extract_resume_information(cv)

    assert result["experience"] == ["3 years of experience"]
    assert result["technical_skills"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert result["education"] == []
    assert result["contact"]["email"] is None
    assert result["contact"]["phone"] is None


def test_consigna_example_mary_jane_watson():
    """Test the reference example for Mary Jane Watson (Machine Learning) from the assignment."""
    cv = """Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."""

    result = extract_resume_information(cv)

    assert result["experience"] == ["2 years of experience"]
    assert result["technical_skills"] == [
        "Python",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "SQL",
        "Git",
    ]


def test_sample_file_from_data_examples():
    """Test that the sample resume file in data/examples can be processed correctly."""
    example_path = Path("data/examples/sample_resume.txt")
    assert example_path.exists(), "Sample file data/examples/sample_resume.txt must exist"

    content = example_path.read_text(encoding="utf-8")
    result = extract_resume_information(content)

    assert result["contact"]["email"] == "wednesday.addams@example.com"
    assert result["contact"]["phone"] == "+1-555-0199"
    assert "3 years of experience" in result["experience"]
    assert "Bachelor's degree" in result["education"]
    assert "Computer Science" in result["education"]
    assert result["technical_skills"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
