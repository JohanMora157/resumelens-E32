"""Etapa 2 - Normalización: traduce SIEMPRE con los FST (nunca con un diccionario)."""

import re
import unicodedata
from typing import List, Optional, Tuple

from src.normalization.transducers import load_fsts

_FSTS = load_fsts()


def clean_token(raw: str) -> str:
    """Limpia ruido de formato ANTES de entrar al FST (el FST solo ve letras del alias).

    - Unicode NFKC (espacios raros, guiones tipográficos).
    - Espacios múltiples -> uno solo.
    - Quita viñetas/paréntesis/comillas al inicio y puntuación al final ("Git." -> "Git").
    Conserva los puntos internos ("Node.js") porque forman parte de los alias.
    """
    token = unicodedata.normalize("NFKC", raw)
    token = token.replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-")
    token = re.sub(r"\s+", " ", token)
    token = re.sub(r"^[\s\-*\u2022\u00b7()\[\]\"']+", "", token)
    token = re.sub(r"[\s.,;:!?()\[\]\"']+$", "", token)
    return token


def normalize_skill(raw: str) -> Optional[str]:
    """Pasa una skill cruda por los FST. Devuelve el token canónico o None."""
    word = list(clean_token(raw))
    if not word:
        return None
    for fst in _FSTS.values():
        outputs = list(fst.translate(word))
        if outputs and outputs[0]:
            return str(outputs[0][0])
    return None


def normalize(raw_skills: List[str]) -> Tuple[List[str], List[str]]:
    """Devuelve (canónicas sin repetir, desconocidas)."""
    known: List[str] = []
    unknown: List[str] = []
    for skill in raw_skills:
        canonical = normalize_skill(skill)
        if canonical is None:
            if skill not in unknown:
                unknown.append(skill)
        elif canonical not in known:
            known.append(canonical)
    return known, unknown


def normalize_qualifications(qualifications) -> List[str]:
    """Interfaz para el pipeline: devuelve solo las skills canónicas (sin repetir)."""
    known, _unknown = normalize(list(qualifications))
    return known


def normalize_with_trace(raw_skills: List[str]) -> List[dict]:
    """Normaliza conservando la trazabilidad: qué texto produjo qué token.

    Devuelve [{"raw": "Postgres", "canonical": "POSTGRESQL", "family": "DATABASES"}, ...].
    Si no se reconoce: canonical = None, family = None.
    """
    trace: List[dict] = []
    for raw in raw_skills:
        word = list(clean_token(raw))
        entry = {"raw": raw, "canonical": None, "family": None}
        if word:
            for family, fst in _FSTS.items():
                outputs = list(fst.translate(word))
                if outputs and outputs[0]:
                    entry["canonical"] = str(outputs[0][0])
                    entry["family"] = family
                    break
        trace.append(entry)
    return trace