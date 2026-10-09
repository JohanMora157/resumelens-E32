"""Etapa 4 - Constructor del DSL: datos del pipeline -> texto en el lenguaje de resume.tx.

SOLO escribe texto. No decide nada de las etapas anteriores y no valida: la validación
la hace textX (validator.py). Los valores que no cumplen las reglas léxicas de la
gramática (correo o teléfono mal formados, skills que no son MAYÚSCULAS_CON_GUION) se
omiten en vez de producir un programa inválido.
"""

import re
from typing import Dict, Iterable, List, Optional

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"[+(]?[0-9][0-9 ().\-]{5,24}[0-9]")
SKILL_RE = re.compile(r"[A-Z][A-Z0-9_]*")

PROFILE_ORDER = [
    "FULL_STACK_DEVELOPER",
    "MACHINE_LEARNING_ENGINEER",
    "QA_ENGINEER",
    "DATA_ANALYST",
]

_WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _quote(text: str) -> str:
    """Escribe un STRING de textX: una sola línea, sin barras invertidas y con comillas escapadas.

    textX solo interpreta la secuencia \" dentro de un STRING, así que las barras invertidas
    se eliminan (no tienen sentido en un nombre ni en un título) y las comillas se escapan.
    """
    text = re.sub(r"\s+", " ", str(text).replace("\\", "")).strip()
    return '"' + text.replace('"', '\\"') + '"'


def parse_years(mention: str) -> Optional[int]:
    """'3 years of experience' -> 3 ; '5+ años de experiencia' -> 5 ; 'two years ...' -> 2."""
    match = re.search(r"\d+", mention)
    if match:
        return int(match.group())

    for word, value in _WORD_NUMBERS.items():
        if re.search(rf"\b{word}\b", mention, re.IGNORECASE):
            return value

    return None


def build_dsl(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    experience: Iterable[str] = (),
    education: Iterable[str] = (),
    skills: Iterable[str] = (),
    classification: Optional[Dict[str, str]] = None,
) -> str:
    """Devuelve el texto del perfil del candidato en el DSL."""

    lines: List[str] = [
        f"candidate {_quote(name or 'Unknown Candidate')} {{"
    ]

    contact: List[str] = []

    if email and EMAIL_RE.fullmatch(email.strip()):
        contact.append(f"email: {email.strip()}")

    if phone and PHONE_RE.fullmatch(phone.strip()):
        contact.append(f"phone: {phone.strip()}")

    lines.append(
        f"  contact {{ {'  '.join(contact)} }}".replace("{  }", "{ }")
    )

    for mention in experience:
        years = parse_years(mention)
        if years is not None:
            lines.append(f"  experience {{ years: {years} }}")

    entries = ", ".join(
        _quote(e) for e in dict.fromkeys(education)
    )

    lines.append(
        f"  education {{ {entries} }}"
        if entries
        else "  education { }"
    )

    clean_skills = [
        s for s in dict.fromkeys(skills)
        if SKILL_RE.fullmatch(s)
    ]

    lines.append(
        f"  skills {{ {', '.join(clean_skills)} }}"
        if clean_skills
        else "  skills { }"
    )

    lines.append("  classification {")

    results = classification or {}

    for profile in PROFILE_ORDER:
        if profile in results:
            lines.append(
                f"    {profile}: {results[profile]}"
            )

    lines.append("  }")
    lines.append("}")

    return "\n".join(lines) + "\n"
