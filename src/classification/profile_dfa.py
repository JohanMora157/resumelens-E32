"""Constructor GENERAL de DFAs por perfil (una sola solución para los 4 perfiles).

Formalización  M = (Q, Σ, δ, q0, F)
  Sea C el conjunto de categorías OBLIGATORIAS del perfil (k = |C|).
  - Q  = P(C): los 2^k subconjuntos de categorías ya cubiertas.
  - Σ  = todos los tokens canónicos del perfil (obligatorios y opcionales).
  - q0 = ∅ (ninguna categoría cubierta).
  - F  = {C} (todas las obligatorias cubiertas).
  - δ(S, t) = S ∪ {cat(t)}   si cat(t) es obligatoria.
    δ(S, t) = S              si cat(t) es opcional (self-loop).
    δ(S, t) indefinida       si t ∉ Σ  -> rechazo inmediato (DFA parcial).

Tipo: DFA (parcial). Para cada estado y cada símbolo hay A LO SUMO una transición,
no hay transiciones ε. Como el estado recuerda QUÉ se cubrió y no EN QUÉ ORDEN,
cualquier permutación de skills válidas se acepta.
"""

import itertools
from typing import Callable, Dict, Iterable, Optional, Sequence

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol


def _name(subset: frozenset, mandatory: Sequence[str], profile: Optional[Dict] = None) -> str:
    if not subset:
        return "q_empty"
    if profile:
        aliases = profile.get("state_aliases") or profile.get("category_aliases")
        if aliases:
            if subset == frozenset(mandatory):
                return profile.get("final_state_name", "q_all_mandatory")
            parts = [aliases[c] for c in mandatory if c in subset]
            return "q_" + "_".join(parts)
    if subset == frozenset(mandatory):
        return "q_all"
    return "q_" + "+".join(c for c in mandatory if c in subset)


def mandatory_categories(profile: Dict, optional: Iterable[str] = ()) -> list:
    optional = set(optional)
    return [c for c in profile["canonical_order"] if c not in optional]


def build_profile_dfa(
    profile: Dict,
    optional: Iterable[str] = (),
    state_namer: Optional[Callable[[frozenset, Sequence[str]], str]] = None,
) -> DeterministicFiniteAutomaton:
    """Construye el DFA de un perfil. `optional` = categorías que no son obligatorias."""
    optional = set(optional)
    unknown = optional - set(profile["categories"])
    if unknown:
        raise ValueError(f"Categorías opcionales inexistentes en el perfil: {sorted(unknown)}")

    categories = profile["categories"]
    mandatory = mandatory_categories(profile, optional)

    namer = state_namer or profile.get("state_namer") or (lambda s, m: _name(s, m, profile))

    subsets = [frozenset(c) for r in range(len(mandatory) + 1)
               for c in itertools.combinations(mandatory, r)]
    states = {s: State(namer(s, mandatory)) for s in subsets}

    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(states[frozenset()])
    dfa.add_final_state(states[frozenset(mandatory)])

    for subset, state in states.items():
        for cat in mandatory:
            for token in categories[cat]:
                dfa.add_transition(state, Symbol(token), states[subset | {cat}])
        for cat in optional:
            for token in categories[cat]:
                dfa.add_transition(state, Symbol(token), state)
    return dfa


def accepts(dfa: DeterministicFiniteAutomaton, skills: Iterable[str]) -> bool:
    """True si el DFA acepta la secuencia. La secuencia vacía se rechaza."""
    skills = list(skills)
    return bool(skills) and dfa.accepts([Symbol(s) for s in skills])
