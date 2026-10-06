"""Resume information extraction module using regular expressions.

Stage 1 of the ResumeLens pipeline.
Identifies and extracts relevant resume text (contact, experience, education,
and technical skills) without normalization, classification, or grammar validation.
"""

import re
from typing import Any, Dict, List

# Pattern for email addresses.
EMAIL_PATTERN: re.Pattern = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Pattern for phone numbers with optional international code, area code, and delimiters.
PHONE_PATTERN: re.Pattern = re.compile(
    r"(?:(?:\b(?:Phone|Tel|Telephone|Mobile|Celular|Cel|Teléfono)\b\s*[:\s]*)?"
    r"(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(\d{2,4}\)|\b\d{2,4}\b)[\s.-]?"
    r"\d{3,4}(?:[\s.-]?\d{3,4})?\b)"
)

# Prefix pattern to strip phone labels.
PHONE_LABEL_PREFIX: re.Pattern = re.compile(
    r"^(?:Phone|Tel|Telephone|Mobile|Celular|Cel|Teléfono)\b\s*[:\s]*",
    re.IGNORECASE,
)

# Pattern for explicit professional experience mentions.
EXPERIENCE_PATTERN: re.Pattern = re.compile(
    r"\b(?:\d+\+?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*"
    r"(?:years?|yrs?|a[ñn]os?)\s*"
    r"(?:(?:of|de)\s*)?"
    r"(?:(?:professional|work|hands-on|laboral)\s*)?"
    r"(?:experience|experiencia)\b",
    re.IGNORECASE,
)

# Pattern for recognized academic degrees and titles.
ACADEMIC_DEGREES_PATTERN: str = (
    r"\b(?:"
    r"Bachelor(?:\'s)?(?:\s+degree)?(?:\s+of\s+[A-Za-z]+)?|"
    r"Master(?:\'s)?(?:\s+degree)?(?:\s+of\s+[A-Za-z]+)?|"
    r"Ph\.?D\.?|Doctorate|Doctorado|"
    r"Associate(?:\'s)?(?:\s+degree)?|"
    r"Licenciatura(?:\s+en\s+[A-Za-z\s]+)?"
    r")\b"
)

# Pattern for common academic fields of study.
ACADEMIC_FIELDS_PATTERN: str = (
    r"\b(?:"
    r"Computer\s+Science|"
    r"Software\s+Engineering|"
    r"Data\s+Science|"
    r"Information\s+Technology|"
    r"Artificial\s+Intelligence|"
    r"Ingenier[ií]a\s+de\s+(?:Sistemas|Software|Computaci[oó]n|Inform[aá]tica|Datos)|"
    r"Ciencias\s+de\s+la\s+Computaci[oó]n"
    r")\b"
)

# Combined pattern for academic education.
EDUCATION_PATTERN: re.Pattern = re.compile(
    f"{ACADEMIC_DEGREES_PATTERN}|{ACADEMIC_FIELDS_PATTERN}",
    re.IGNORECASE,
)

# Pattern for technical skills section headers and content capture.
SKILLS_SECTION_PATTERN: re.Pattern = re.compile(
    r"(?:^|\n)\s*"
    r"(?:Technical\s+Skills?|Skills?|Technologies|Programming\s+Languages|"
    r"Frameworks(?:\s+(?:and|&)\s+Libraries)?|Databases?|Tools(?:\s+(?:and|&)\s+Technologies)?|Tech\s+Stack)"
    r"(?:\s*:|\s*(?=\n))"
    r"(?P<content>[\s\S]*?)"
    r"(?=(?:\n\s*(?:Technical\s+Skills?|Skills?|Technologies|Programming\s+Languages|"
    r"Frameworks|Databases?|Tools|Tech\s+Stack|"
    r"Education|Academic|Experience|Professional\s+Experience|Work\s+Experience|"
    r"Projects|Certifications?|Contact|Summary|Profile|References|About\s+Me)\s*[:\n]|\n\s*\n\s*\n|\Z))",
    re.IGNORECASE,
)

# Delimiters for skills within a section: commas, semicolons, pipes, and newlines.
SKILL_DELIMITERS_PATTERN: re.Pattern = re.compile(r"[,;|\n]+")


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract email addresses and phone numbers from resume text.

    Args:
        text (str): Raw resume text.

    Returns:
        Dict[str, Any]: Dictionary containing detected emails and phone numbers.
    """
    emails: List[str] = EMAIL_PATTERN.findall(text)

    raw_phones: List[str] = PHONE_PATTERN.findall(text)
    phones: List[str] = []
    for raw in raw_phones:
        cleaned = PHONE_LABEL_PREFIX.sub("", raw).strip()
        if cleaned and cleaned not in phones:
            phones.append(cleaned)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "emails": emails,
        "phones": phones,
    }


def extract_experience(text: str) -> List[str]:
    """Extract explicit professional experience mentions.

    Args:
        text (str): Raw resume text.

    Returns:
        List[str]: List of unique experience mentions.
    """
    matches: List[str] = EXPERIENCE_PATTERN.findall(text)
    experience_list: List[str] = []
    for exp in matches:
        cleaned = exp.strip()
        if cleaned and cleaned not in experience_list:
            experience_list.append(cleaned)
    return experience_list


def extract_education(text: str) -> List[str]:
    """Extract recognized academic degrees and fields of study in their original text.

    Args:
        text (str): Raw resume text.

    Returns:
        List[str]: List of unique education mentions.
    """
    education_list: List[str] = []
    for match in EDUCATION_PATTERN.finditer(text):
        term = match.group(0).strip()
        if term and term not in education_list:
            education_list.append(term)
    return education_list


def extract_technical_skills(text: str) -> List[str]:
    """Extract technical skills and qualifications listed in recognized sections.

    Preserves original token representations without normalization.

    Args:
        text (str): Raw resume text.

    Returns:
        List[str]: List of extracted skills in original text form.
    """
    skills: List[str] = []

    for section in SKILLS_SECTION_PATTERN.finditer(text):
        content = section.group("content").strip()
        raw_tokens = SKILL_DELIMITERS_PATTERN.split(content)
        for token in raw_tokens:
            # Strip leading bullets, dashes, numbers, or dots
            cleaned = re.sub(r"^[\s\-*•·\d\.)]+", "", token)
            # Strip trailing punctuation while keeping extensions like .js or .net
            cleaned = re.sub(r"[\s,;.]+$", "", cleaned).strip()
            if cleaned and cleaned not in skills:
                skills.append(cleaned)

    return skills


def extract_resume_information(text: str) -> Dict[str, Any]:
    """Extract relevant resume information using regular expressions.

    Separates the following categories:
    - contact: detected emails and phone numbers.
    - experience: list of explicit experience mentions.
    - education: list of academic qualifications in original text.
    - technical_skills: list of skills and technologies in original text.

    Args:
        text (str): Raw resume text.

    Returns:
        Dict[str, Any]: Structured dictionary with extracted data.
    """
    if not text:
        return {
            "contact": {
                "email": None,
                "phone": None,
                "emails": [],
                "phones": [],
            },
            "experience": [],
            "education": [],
            "technical_skills": [],
        }

    contact = extract_contact_info(text)
    experience = extract_experience(text)
    education = extract_education(text)
    technical_skills = extract_technical_skills(text)

    return {
        "contact": contact,
        "experience": experience,
        "education": education,
        "technical_skills": technical_skills,
    }
