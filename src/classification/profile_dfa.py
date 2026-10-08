"""Constructor general de autómatas finitos deterministas (DFA) para perfiles de ResumeLens.

Implementa la formalización M = (Q, Σ, δ, q0, F) basada en el conjunto potencia
(powerset construction) de las categorías obligatorias del perfil.

- Q: Estados que representan todos los subconjuntos de categorías obligatorias satisfechas.
- Σ: Todos los tokens canónicos pertenecientes a las categorías del perfil.
- δ: Transición de estados:
     * Categorías obligatorias: avanzan al estado unión S ∪ {C}.
     * Categorías opcionales: auto-bucle (self-loop) en cada estado.
     * Símbolos ajenos a Σ: sin transición definida (rechazo).
- q0: q_empty (ninguna categoría obligatoria cumplida).
- F: {q_all_mandatory} (todas las categorías obligatorias cumplidas).
"""

from typing import Dict, Iterable, Sequence
import itertools

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol


def _category_alias(cat: str) -> str:
    """Obtiene un identificador corto y legible para el estado."""
    return cat.lower().replace("_language", "").replace("_testing", "").replace("_processing", "")


def _subset_to_state_name(subset: frozenset, mandatory_categories: Sequence[str]) -> str:
    if not subset:
        return "q_empty"
    if subset == frozenset(mandatory_categories):
        return "q_all_mandatory"
    parts = [
        _category_alias(cat)
        for cat in sorted(subset, key=lambda c: mandatory_categories.index(c))
    ]
    return "q_" + "_".join(parts)


def build_profile_dfa(
    profile: Dict,
    optional: Iterable[str] = (),
) -> DeterministicFiniteAutomaton:
    """Construye un DFA determinista e independiente del orden para un perfil.

    Args:
        profile: Definición del perfil (con 'canonical_order' y 'categories').
        optional: Secuencia de nombres de categorías opcionales (auto-bucles).

    Returns:
        DeterministicFiniteAutomaton: Instancia de pyformlang configurada.
    """
    dfa = DeterministicFiniteAutomaton()

    categories = profile["categories"]
    optional_set = set(optional)
    mandatory_categories = [c for c in profile["canonical_order"] if c not in optional_set]

    # 1. Generar todos los estados a partir del conjunto potencia de categorías obligatorias
    subsets = []
    for r in range(len(mandatory_categories) + 1):
        for combo in itertools.combinations(mandatory_categories, r):
            subsets.append(frozenset(combo))

    state_map = {
        s: State(_subset_to_state_name(s, mandatory_categories))
        for s in subsets
    }

    # 2. Configurar estado inicial y final
    q0 = state_map[frozenset()]
    q_final = state_map[frozenset(mandatory_categories)]
    dfa.add_start_state(q0)
    dfa.add_final_state(q_final)

    # 3. Configurar transiciones
    for s, state_obj in state_map.items():
        # Categorías obligatorias: avanzan al estado unión
        for cat in mandatory_categories:
            next_s = s | {cat}
            next_state_obj = state_map[next_s]
            for token in categories[cat]:
                dfa.add_transition(state_obj, Symbol(token), next_state_obj)

        # Categorías opcionales: auto-bucle preservando el estado
        for cat in optional_set:
            if cat in categories:
                for token in categories[cat]:
                    dfa.add_transition(state_obj, Symbol(token), state_obj)

    return dfa


def accepts(dfa: DeterministicFiniteAutomaton, skills: Iterable[str]) -> bool:
    """Evalúa si una secuencia de tokens canónicos es aceptada por el DFA.

    Args:
        dfa: Autómata finito determinista del perfil.
        skills: Secuencia de tokens canónicos de habilidades.

    Returns:
        bool: True si alcanza el estado final de aceptación, False en caso contrario.
    """
    skill_list = list(skills)
    if not skill_list:
        return False
    symbols = [Symbol(s) for s in skill_list]
    return dfa.accepts(symbols)
