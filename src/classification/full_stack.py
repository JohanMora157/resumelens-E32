"""Módulo de clasificación para el perfil de Full Stack Developer.

Implementación en progreso del Autómata Finito Determinista (DFA)
para el reconocimiento de cualificaciones de Full Stack Developer.
"""

from typing import Any, Dict
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from src.classification.profiles import FULL_STACK_DEVELOPER

# Definición del perfil y categorías para Full Stack Developer
FULL_STACK_PROFILE: Dict[str, Any] = {
    "name": FULL_STACK_DEVELOPER,
    "canonical_order": [
        "LANGUAGES",
        "FRONTEND",
        "BACKEND",
        "API",
        "DATABASES",
        "VERSION_CONTROL",
    ],
    "categories": {
        "LANGUAGES": ["JAVASCRIPT", "TYPESCRIPT"],
        "FRONTEND": ["REACT", "ANGULAR", "VUE"],
        "BACKEND": ["NODE_JS", "DJANGO", "SPRING_BOOT"],
        "API": ["REST_API"],
        "DATABASES": ["POSTGRESQL", "MYSQL", "MONGODB", "SQL"],
        "VERSION_CONTROL": ["GIT"],
    },
}

# Estados del autómata
STATE_START = "q0"
STATE_LANG = "q_lang"
STATE_FRONT = "q_front"
STATE_BACK = "q_back"
STATE_API = "q_api"
STATE_DB = "q_db"
STATE_GIT = "q_git"


def build_full_stack_automaton() -> DeterministicFiniteAutomaton:
    """Construye la estructura inicial del DFA para Full Stack Developer.

    Inicializa los estados y transiciones para las primeras capas (lenguaje y frontend).
    """
    dfa = DeterministicFiniteAutomaton()

    s_start = State(STATE_START)
    s_lang = State(STATE_LANG)
    s_front = State(STATE_FRONT)

    dfa.add_start_state(s_start)

    # 1. Capa de Lenguajes: q0 -> q_lang
    for token in FULL_STACK_PROFILE["categories"]["LANGUAGES"]:
        sym = Symbol(token)
        dfa.add_transition(s_start, sym, s_lang)
        dfa.add_transition(s_lang, sym, s_lang)

    # 2. Capa Frontend: q_lang -> q_front
    for token in FULL_STACK_PROFILE["categories"]["FRONTEND"]:
        sym = Symbol(token)
        dfa.add_transition(s_lang, sym, s_front)
        dfa.add_transition(s_front, sym, s_front)

    # TODO: Añadir transiciones para backend, API, databases y estado de aceptación git
    return dfa
