"""Módulo de clasificación para el perfil de Full Stack Developer.

Implementación del Autómata Finito Determinista (DFA) completo
para el reconocimiento formal de cualificaciones de Full Stack Developer.
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
    """Construye y retorna el DFA completo para Full Stack Developer.

    Formal 5-tuple:
        M = (Q, Σ, δ, q0, F)
    donde:
        Q  = {q0, q_lang, q_front, q_back, q_api, q_db, q_git}
        Σ  = {JAVASCRIPT, TYPESCRIPT, REACT, ANGULAR, VUE, NODE_JS,
              DJANGO, SPRING_BOOT, REST_API, POSTGRESQL, MYSQL,
              MONGODB, SQL, GIT}
        q0 = 'q0'
        F  = {'q_git'}
        δ  = función de transición que modela la progresión de capas canónicas.
    """
    dfa = DeterministicFiniteAutomaton()

    s_start = State(STATE_START)
    s_lang = State(STATE_LANG)
    s_front = State(STATE_FRONT)
    s_back = State(STATE_BACK)
    s_api = State(STATE_API)
    s_db = State(STATE_DB)
    s_git = State(STATE_GIT)

    dfa.add_start_state(s_start)
    dfa.add_final_state(s_git)

    # 1. Capa de Lenguajes: q0 -> q_lang (con auto-bucle para múltiples lenguajes)
    for token in FULL_STACK_PROFILE["categories"]["LANGUAGES"]:
        sym = Symbol(token)
        dfa.add_transition(s_start, sym, s_lang)
        dfa.add_transition(s_lang, sym, s_lang)

    # 2. Capa Frontend: q_lang -> q_front (con auto-bucle para múltiples frameworks)
    for token in FULL_STACK_PROFILE["categories"]["FRONTEND"]:
        sym = Symbol(token)
        dfa.add_transition(s_lang, sym, s_front)
        dfa.add_transition(s_front, sym, s_front)

    # 3. Capa Backend: q_front -> q_back (con auto-bucle para múltiples tecnologías backend)
    for token in FULL_STACK_PROFILE["categories"]["BACKEND"]:
        sym = Symbol(token)
        dfa.add_transition(s_front, sym, s_back)
        dfa.add_transition(s_back, sym, s_back)

    # 4. Capa API (opcional): q_back -> q_api (con auto-bucle)
    for token in FULL_STACK_PROFILE["categories"]["API"]:
        sym = Symbol(token)
        dfa.add_transition(s_back, sym, s_api)
        dfa.add_transition(s_api, sym, s_api)

    # 5. Capa Bases de Datos: q_back -> q_db (saltando API) o q_api -> q_db
    for token in FULL_STACK_PROFILE["categories"]["DATABASES"]:
        sym = Symbol(token)
        dfa.add_transition(s_back, sym, s_db)
        dfa.add_transition(s_api, sym, s_db)
        dfa.add_transition(s_db, sym, s_db)

    # 6. Capa Control de Versiones: q_db -> q_git (estado final de aceptación)
    for token in FULL_STACK_PROFILE["categories"]["VERSION_CONTROL"]:
        sym = Symbol(token)
        dfa.add_transition(s_db, sym, s_git)
        dfa.add_transition(s_git, sym, s_git)

    return dfa
