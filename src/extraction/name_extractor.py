"""Etapa 1 - Nombre del candidato con expresiones regulares (lo necesita la gramática).

Un nombre es una línea (entre las primeras no vacías) de 2 a 5 palabras formadas solo por
letras (con tildes), apóstrofes, guiones o puntos, cada una con inicial mayúscula (salvo
partículas como "de", "van" o "del"), y que no es un encabezado de sección.
"""

import re
from typing import Optional

NAME_PATTERN: re.Pattern = re.compile(r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+){1,4}$", re.UNICODE)

_HEADERS = {"technical", "skills", "skill", "education", "experience", "contact", "summary", "profile",
            "projects", "certifications", "habilidades", "educación", "experiencia", "resumen", "perfil",
            "technologies", "tools", "databases", "contacto", "references", "languages"}


_PARTICLES = {"de", "del", "la", "las", "los", "y", "van", "von", "der", "da", "di", "bin", "al"}


def _looks_like_name(line: str) -> bool:
    words = re.split(r"[ ]+", line)
    return all(w[0].isupper() or w.lower() in _PARTICLES for w in words)


def extract_name(text: str, max_lines: int = 3) -> Optional[str]:
    """Devuelve el nombre del candidato o None."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    for line in lines[:max_lines]:
        if NAME_PATTERN.fullmatch(line) and _looks_like_name(line) and not (set(re.split(r"[ '\-.]", line.lower())) & _HEADERS):
            return line
    return None