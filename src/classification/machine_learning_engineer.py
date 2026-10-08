"""DFA del perfil Machine Learning Engineer.

Se construye con el constructor general (profile_dfa.build_profile_dfa), por lo que
sigue exactamente la misma formalización M = (Q, Σ, δ, q0, F) que los demás perfiles.

Categorías opcionales (self-loop, no hace falta cubrirlas): ()
"""

from typing import Iterable

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.profile_dfa import accepts, build_profile_dfa
from src.classification.profiles import MACHINE_LEARNING_ENGINEER

OPTIONAL_CATEGORIES = ()


def build_ml_engineer_dfa() -> DeterministicFiniteAutomaton:
    """Construye el DFA de Machine Learning Engineer."""
    return build_profile_dfa(MACHINE_LEARNING_ENGINEER, optional=OPTIONAL_CATEGORIES)


_DFA: DeterministicFiniteAutomaton = build_ml_engineer_dfa()


def classify_ml_engineer(skills: Iterable[str]) -> bool:
    """True si las skills canónicas (en cualquier orden) satisfacen el perfil."""
    return accepts(_DFA, skills)
