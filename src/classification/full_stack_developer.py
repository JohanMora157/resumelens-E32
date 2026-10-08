"""DFA del perfil Full Stack Developer.

Se construye con el constructor general (profile_dfa.build_profile_dfa), por lo que
sigue exactamente la misma formalización M = (Q, Σ, δ, q0, F) que los demás perfiles.

Categorías opcionales (self-loop, no hace falta cubrirlas): ("API",)
"""

from typing import Iterable

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.profile_dfa import accepts, build_profile_dfa
from src.classification.profiles import FULL_STACK_DEVELOPER

OPTIONAL_CATEGORIES = ("API",)


def build_full_stack_dfa() -> DeterministicFiniteAutomaton:
    """Construye el DFA de Full Stack Developer."""
    return build_profile_dfa(FULL_STACK_DEVELOPER, optional=OPTIONAL_CATEGORIES)


_DFA: DeterministicFiniteAutomaton = build_full_stack_dfa()


def classify_full_stack(skills: Iterable[str]) -> bool:
    """True si las skills canónicas (en cualquier orden) satisfacen el perfil."""
    return accepts(_DFA, skills)
