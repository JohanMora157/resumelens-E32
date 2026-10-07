"""Deterministic Finite Automaton (DFA) for the Data Analyst profile.

Recognizes qualification patterns for Data Analyst:
- Mandatory: at least one QUERY_LANGUAGE (SQL, POSTGRESQL, MYSQL)
- Optional: SPREADSHEET (EXCEL)
- Mandatory: at least one ANALYSIS_LANGUAGE (PYTHON, R)
- Mandatory: at least one DATA_PROCESSING (PANDAS, NUMPY)
- Mandatory: at least one VISUALIZATION (POWER_BI, TABLEAU, MATPLOTLIB)

Formal 5-tuple: M = (Q, Sigma, delta, q0, F)
- Alphabet Sigma: 11 canonical skill tokens belonging to the Data Analyst profile.
- States Q: 16 states representing the powerset of satisfied mandatory categories:
  P({QUERY, ANALYSIS, PROCESSING, VISUALIZATION}).
- Start state q0: q_empty (no mandatory categories satisfied yet).
- Final state F: {q_all_mandatory} (all 4 mandatory categories satisfied).
- Transition function delta:
  - Reading a mandatory category token transitions to the union of currently
    satisfied categories and that new category.
  - Reading an optional SPREADSHEET token (EXCEL) performs a self-loop on the
    current state, preserving existing category progress.
  - Reading any foreign token (not in Sigma) has no transition defined,
    causing immediate rejection.

Order Independence:
Because skills in a candidate's resume appear in arbitrary sequence, the DFA tracks
the subset of satisfied mandatory categories rather than enforcing a rigid linear
order. Thus, any permutation of valid skills containing the mandatory categories
is accepted.
"""

from typing import Iterable, List
import itertools

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from src.classification.profiles import DATA_ANALYST

MANDATORY_CATEGORIES = (
    "QUERY_LANGUAGE",
    "ANALYSIS_LANGUAGE",
    "DATA_PROCESSING",
    "VISUALIZATION",
)

OPTIONAL_CATEGORIES = ("SPREADSHEET",)

_CATEGORY_ALIASES = {
    "QUERY_LANGUAGE": "query",
    "ANALYSIS_LANGUAGE": "analysis",
    "DATA_PROCESSING": "processing",
    "VISUALIZATION": "visualization",
}


def _subset_to_state_name(subset: frozenset) -> str:
    if not subset:
        return "q_empty"
    if subset == frozenset(MANDATORY_CATEGORIES):
        return "q_all_mandatory"
    parts = [
        _CATEGORY_ALIASES[cat]
        for cat in sorted(subset, key=lambda c: MANDATORY_CATEGORIES.index(c))
    ]
    return "q_" + "_".join(parts)


def build_data_analyst_dfa() -> DeterministicFiniteAutomaton:
    """Build and return the order-independent Deterministic Finite Automaton for Data Analyst.

    Formal 5-tuple: M = (Q, Sigma, delta, q0, F)
    - Q: 16 states representing all subsets of {QUERY, ANALYSIS, PROCESSING, VISUALIZATION}
    - Sigma: 11 canonical skills across the 5 categories
    - delta: state transition function
    - q0: q_empty
    - F: {q_all_mandatory}
    """
    dfa = DeterministicFiniteAutomaton()

    categories = DATA_ANALYST["categories"]

    # 1. Generate all 16 states from powerset of mandatory categories
    subsets = []
    for r in range(len(MANDATORY_CATEGORIES) + 1):
        for combo in itertools.combinations(MANDATORY_CATEGORIES, r):
            subsets.append(frozenset(combo))

    state_map = {s: State(_subset_to_state_name(s)) for s in subsets}

    # 2. Configure start and final states
    q0 = state_map[frozenset()]
    q_final = state_map[frozenset(MANDATORY_CATEGORIES)]
    dfa.add_start_state(q0)
    dfa.add_final_state(q_final)

    # 3. Add transitions for all states and category tokens
    for s, state_obj in state_map.items():
        # Mandatory categories: advance to union state
        for cat in MANDATORY_CATEGORIES:
            next_s = s | {cat}
            next_state_obj = state_map[next_s]
            for token in categories[cat]:
                dfa.add_transition(state_obj, Symbol(token), next_state_obj)

        # Optional categories (SPREADSHEET): self-loop preserving state
        for cat in OPTIONAL_CATEGORIES:
            next_state_obj = state_obj
            for token in categories[cat]:
                dfa.add_transition(state_obj, Symbol(token), next_state_obj)

    return dfa


# Cached instance for efficient reuse
_DATA_ANALYST_DFA: DeterministicFiniteAutomaton = build_data_analyst_dfa()


def classify_data_analyst(skills: Iterable[str]) -> bool:
    """Classify whether a sequence of canonical skills satisfies the Data Analyst profile.

    The sequence can appear in any order. The candidate must satisfy:
    - At least one QUERY_LANGUAGE (SQL, POSTGRESQL, MYSQL)
    - At least one ANALYSIS_LANGUAGE (PYTHON, R)
    - At least one DATA_PROCESSING (PANDAS, NUMPY)
    - At least one VISUALIZATION (POWER_BI, TABLEAU, MATPLOTLIB)
    - Optional SPREADSHEET (EXCEL) is accepted anywhere
    - Any foreign skill not in the profile leads to rejection

    Args:
        skills: Sequence of canonical skill tokens.

    Returns:
        bool: True if accepted by the Data Analyst DFA, False otherwise.
    """
    skill_list = list(skills)
    if not skill_list:
        return False
    symbols = [Symbol(s) for s in skill_list]
    return _DATA_ANALYST_DFA.accepts(symbols)

