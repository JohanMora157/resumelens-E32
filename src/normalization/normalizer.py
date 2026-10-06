"""Etapa 2 - Normalización: traduce SIEMPRE con los FST (nunca con un diccionario)."""

from typing import List, Optional, Tuple

from src.normalization.transducers import load_fsts

_FSTS = load_fsts()


def normalize_skill(raw: str) -> Optional[str]:
    """Pasa una skill cruda por los FST. Devuelve el token canónico o None."""
    word = list(raw.strip())
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