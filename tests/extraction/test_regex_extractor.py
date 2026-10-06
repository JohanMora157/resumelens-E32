"""Unit tests for the regular expression extraction module (Stage 1).

Verifies extraction of:
1. Email addresses (standard, subdomains, plus-tags, multi-level TLDs)
2. Phone numbers (international, parenthesis area code, dots, dashes, labeled plain digits)
3. Explicit professional experience mentions (English and Spanish)
4. Technical skills section headers (English and Spanish, with or without colons)
5. Multiple skills across various delimiters (, ; | \\n) and spacing
6. Academic degrees and fields of study
7. Full resume with multiple categories simultaneously
8. Resume with missing categories without errors
9. Strict preservation of original token casing and representation
10. Absence of semantic normalization (Regex is not FST)
11. Assignment reference examples (Wednesday Addams and Mary Jane Watson)
12. Case insensitivity for section headers, degrees, and experience
13. Deduplication of repeated values (emails, skills, experience, degrees)
14. Empty and whitespace-only inputs
15. Spanish language resumes
16. Multi-section resumes with interspersed sections
17. Negative cases where expressions must NOT match (dates, non-emails, general words)
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


def test_extract_email_various_formats():
    """Test extraction of diverse email formats including subdomains, plus-tags, and multi-level TLDs."""
    text = """
    Emails:
    alex.dev+work@sub.domain.co.uk
    contact-support@company.io
    student_123@universidad.edu.co
    """
    contact = extract_contact_info(text)
    assert "alex.dev+work@sub.domain.co.uk" in contact["emails"]
    assert "contact-support@company.io" in contact["emails"]
    assert "student_123@universidad.edu.co" in contact["emails"]


def test_extract_phone_formats():
    """Test extraction of phone numbers across common formatting conventions."""
    formats = [
        ("Phone: +1-555-123-4567", "+1-555-123-4567"),
        ("Tel: (555) 234-5678", "(555) 234-5678"),
        ("Mobile: +57 300 123 4567", "+57 300 123 4567"),
        ("Direct: 555-345-6789", "555-345-6789"),
        ("Phone: 555.456.7890", "555.456.7890"),
        ("Celular: 3109876543", "3109876543"),
        ("Teléfono: +57 (601) 234-5678", "+57 (601) 234-5678"),
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


def test_extract_skills_with_irregular_spacing_and_trailing_punctuation():
    """Test skills separated by mixed delimiters, extra whitespace, and trailing punctuation."""
    text = "Technical Skills:  JS ,   React.js ;   NodeJS  | Postgres , Git.  "
    skills = extract_technical_skills(text)
    assert skills == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


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

    # Whitespace-only text
    res_ws = extract_resume_information("   \n\t   \n  ")
    assert res_ws["contact"]["email"] is None
    assert res_ws["experience"] == []
    assert res_ws["education"] == []
    assert res_ws["technical_skills"] == []

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


def test_case_insensitivity_for_headers_and_patterns():
    """Test that headers, degrees, and experience match regardless of uppercase or lowercase."""
    cv = """
    UPPERCASE CANDIDATE
    CONTACT: CANDIDATE@CORP.COM | TEL: 555-987-6543
    3 YEARS OF EXPERIENCE IN DISTRIBUTED SYSTEMS.

    EDUCATION:
    BACHELOR'S DEGREE IN COMPUTER SCIENCE

    TECHNICAL SKILLS:
    PYTHON, DOCKER, KUBERNETES
    """
    result = extract_resume_information(cv)

    assert result["contact"]["email"] == "CANDIDATE@CORP.COM"
    assert result["contact"]["phone"] == "555-987-6543"
    assert "3 YEARS OF EXPERIENCE" in result["experience"]
    assert any("BACHELOR'S DEGREE" in edu.upper() for edu in result["education"])
    assert any("COMPUTER SCIENCE" in edu.upper() for edu in result["education"])
    assert result["technical_skills"] == ["PYTHON", "DOCKER", "KUBERNETES"]


def test_deduplication_of_repeated_values():
    """Test that repeated skills, emails, and experience are cleanly deduplicated."""
    cv = """
    Dev Candidate
    Email: dev@example.com | Alternate: dev@example.com
    Has 3 years of experience. Repeat: 3 years of experience.

    Programming Languages:
    Python, SQL, Python

    Databases:
    PostgreSQL, SQL
    """
    result = extract_resume_information(cv)

    # Emails deduplicated
    assert result["contact"]["emails"] == ["dev@example.com"]

    # Experience deduplicated
    assert result["experience"] == ["3 years of experience"]

    # Skills deduplicated across sub-sections while preserving first order
    assert result["technical_skills"] == ["Python", "SQL", "PostgreSQL"]


def test_spanish_language_resume():
    """Test extraction of a Spanish language resume with Spanish headers and degree titles."""
    cv = """
    Johan Mora
    Email: johan.mora@example.com | Teléfono: +57 300 123 4567
    Profesional con 3 años de experiencia en desarrollo de software.

    Educación:
    Ingeniería de Sistemas

    Habilidades Técnicas:
    Python, Django, PostgreSQL, Git.
    """
    result = extract_resume_information(cv)

    assert result["contact"]["email"] == "johan.mora@example.com"
    assert result["contact"]["phone"] == "+57 300 123 4567"
    assert result["experience"] == ["3 años de experiencia"]
    assert "Ingeniería de Sistemas" in result["education"]
    assert result["technical_skills"] == ["Python", "Django", "PostgreSQL", "Git"]


def test_resume_with_multiple_interspersed_sections():
    """Test resume with multiple sections in arbitrary order (summary, projects, certs)."""
    cv = """
    Summary:
    Enthusiastic developer with 5+ years of experience.

    Projects:
    Built high-scale web platforms.

    Programming Languages:
    TypeScript, Python

    Certifications:
    AWS Certified Solutions Architect

    Tools & Technologies:
    Docker, Git
    """
    result = extract_resume_information(cv)

    assert result["experience"] == ["5+ years of experience"]
    assert result["technical_skills"] == ["TypeScript", "Python", "Docker", "Git"]


def test_negative_cases_non_matching_expressions():
    """Test text that resembles patterns but should deliberately NOT match."""
    # 1. Non-email text
    text_invalid_email = "Contact user@ without domain or @missinguser.com or invalid-email."
    contact = extract_contact_info(text_invalid_email)
    assert contact["emails"] == []
    assert contact["email"] is None

    # 2. Date ranges and version numbers should NOT match as phone numbers
    text_dates = "Worked from 2018 - 2022 on Python 3.11.9. Zip: 90210."
    contact_dates = extract_contact_info(text_dates)
    assert contact_dates["phones"] == []
    assert contact_dates["phone"] is None

    # 3. Non-experience mentions of the word 'experience'
    text_generic_exp = (
        "Focuses on user experience and customer experience design. "
        "Believes that life experience matters."
    )
    exp = extract_experience(text_generic_exp)
    assert exp == []

    # 4. Non-academic mentions of degrees or science
    text_generic_edu = "Possesses a high degree of enthusiasm in general science."
    edu = extract_education(text_generic_edu)
    assert edu == []

    # 5. Generic words outside of technical skill sections are not captured as skills
    text_general = "I know some programming concepts and use various tools daily."
    skills = extract_technical_skills(text_general)
    assert skills == []
