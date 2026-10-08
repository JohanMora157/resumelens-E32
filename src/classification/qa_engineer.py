"""DFA del perfil QA Engineer.

Se construye con el constructor general (profile_dfa.build_profile_dfa), por lo que
sigue exactamente la misma formalización M = (Q, Σ, δ, q0, F) que los demás perfiles.

Categorías opcionales (self-loop, no hace falta cubrirlas): ()
"""

from typing import Iterable

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.profile_dfa import accepts, build_profile_dfa
from src.classification.profiles import QA_ENGINEER

OPTIONAL_CATEGORIES = ()


def build_qa_engineer_dfa() -> DeterministicFiniteAutomaton:
    """Construye el DFA de QA Engineer."""
    return build_profile_dfa(QA_ENGINEER, optional=OPTIONAL_CATEGORIES)


_DFA: DeterministicFiniteAutomaton = build_qa_engineer_dfa()


def classify_qa_engineer(skills: Iterable[str]) -> bool:
    """True si las skills canónicas (en cualquier orden) satisfacen el perfil."""
    return accepts(_DFA, skills)
