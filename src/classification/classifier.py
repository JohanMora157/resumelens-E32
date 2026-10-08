"""Etapa 3 - Reconocimiento de patrones con autómatas finitos.

classify_candidate recibe las skills canónicas (salida del FST) y devuelve, para cada
uno de los 4 perfiles, ACCEPTED o REJECTED. Para cada perfil:
  1. sort_for_profile ordena y DESCARTA los tokens que no son del perfil
     (los DFA rechazan cualquier símbolo fuera de su alfabeto).
  2. El DFA del perfil decide si se satisface el patrón.
"""

from typing import Callable, Dict, Iterable, List

from src.classification.data_analyst import classify_data_analyst
from src.classification.full_stack_developer import classify_full_stack
from src.classification.machine_learning_engineer import classify_ml_engineer
from src.classification.profiles import PROFILES
from src.classification.qa_engineer import classify_qa_engineer
from src.normalization.sorter import sort_for_profile

ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"

_CLASSIFIERS: Dict[str, Callable[[Iterable[str]], bool]] = {
    "FULL_STACK_DEVELOPER": classify_full_stack,
    "MACHINE_LEARNING_ENGINEER": classify_ml_engineer,
    "QA_ENGINEER": classify_qa_engineer,
    "DATA_ANALYST": classify_data_analyst,
}


def classify_profile(qualifications: Iterable[str], profile_name: str) -> str:
    """ACCEPTED/REJECTED para un solo perfil."""
    if profile_name not in _CLASSIFIERS:
        raise KeyError(f"Perfil desconocido: {profile_name}")
    ordered = sort_for_profile(list(qualifications or []), PROFILES[profile_name])
    return ACCEPTED if _CLASSIFIERS[profile_name](ordered) else REJECTED


def classify_candidate(qualifications: Iterable[str]) -> Dict[str, str]:
    """Resultado para los 4 perfiles: {perfil: "ACCEPTED" | "REJECTED"}."""
    skills = list(qualifications or [])
    return {name: classify_profile(skills, name) for name in _CLASSIFIERS}


def accepted_profiles(qualifications: Iterable[str]) -> List[str]:
    """Nombres de los perfiles aceptados (puede ser ninguno o varios)."""
    return [n for n, r in classify_candidate(qualifications).items() if r == ACCEPTED]