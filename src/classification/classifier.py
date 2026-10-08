"""Módulo de reconocimiento y clasificación de patrones mediante autómatas finitos.

Evalúa cualificaciones frente a los 4 perfiles profesionales:
- FULL_STACK_DEVELOPER
- MACHINE_LEARNING_ENGINEER
- QA_ENGINEER
- DATA_ANALYST
"""

from typing import Any, Dict, List, Optional

from src.classification.profile_dfa import accepts, build_profile_dfa
from src.classification.profiles import (
    DATA_ANALYST,
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    PROFILES,
    QA_ENGINEER,
)
from src.normalization.sorter import sort_for_profile

ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"

PROFILE_ORDER: List[str] = [
    "FULL_STACK_DEVELOPER",
    "MACHINE_LEARNING_ENGINEER",
    "QA_ENGINEER",
    "DATA_ANALYST",
]

_OPTIONAL_CATEGORIES: Dict[str, tuple] = {
    "FULL_STACK_DEVELOPER": ("API",),
    "MACHINE_LEARNING_ENGINEER": (),
    "QA_ENGINEER": (),
    "DATA_ANALYST": ("SPREADSHEET",),
}

_DFAS = {
    name: build_profile_dfa(PROFILES[name], optional=_OPTIONAL_CATEGORIES[name])
    for name in PROFILE_ORDER
}


def classify_profile(qualifications: Optional[Any], profile_name: str) -> str:
    """Evalúa las cualificaciones canónicas frente al DFA de un único perfil.

    Args:
        qualifications: Lista de cualificaciones canónicas (puede ser None o vacía).
        profile_name: Nombre del perfil a evaluar.

    Returns:
        str: ACCEPTED si cumple el perfil, REJECTED si no.

    Raises:
        KeyError: Si el nombre del perfil no existe.
    """
    if profile_name not in PROFILES:
        raise KeyError(f"Perfil desconocido: {profile_name}")

    if not qualifications:
        return REJECTED

    profile_dict = PROFILES[profile_name]
    dfa = _DFAS[profile_name]

    # Orden canónico por perfil y descarte de tokens ajenos
    sorted_skills = sort_for_profile(list(qualifications), profile_dict)
    return ACCEPTED if accepts(dfa, sorted_skills) else REJECTED


def classify_candidate(qualifications: Optional[Any]) -> Dict[str, str]:
    """Evalúa las cualificaciones normalizadas frente a los autómatas de cada perfil profesional.

    Args:
        qualifications: Cualificaciones normalizadas (puede ser None o vacía).

    Returns:
        Dict[str, str]: Diccionario ordenado con el resultado (ACCEPTED/REJECTED) para cada perfil.
    """
    return {name: classify_profile(qualifications, name) for name in PROFILE_ORDER}


def accepted_profiles(qualifications: Optional[Any]) -> List[str]:
    """Devuelve la lista de perfiles que el candidato satisface con éxito."""
    results = classify_candidate(qualifications)
    return [name for name, status in results.items() if status == ACCEPTED]
