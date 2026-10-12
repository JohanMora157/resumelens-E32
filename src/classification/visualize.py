"""Formalización (5-tupla) y diagramas de los 4 DFA, para docs/03_formalization.md.

Uso:  python -m src.classification.visualize
Luego: dot -Tpng docs/diagrams/dfa/dfa_data_analyst.dot -o docs/diagrams/dfa/dfa_data_analyst.png
"""

import sys
from pathlib import Path
from typing import Dict

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.data_analyst import build_data_analyst_dfa
from src.classification.full_stack_developer import build_full_stack_dfa
from src.classification.machine_learning_engineer import build_ml_engineer_dfa
from src.classification.qa_engineer import build_qa_engineer_dfa

BUILDERS = {
    "FULL_STACK_DEVELOPER": build_full_stack_dfa,
    "MACHINE_LEARNING_ENGINEER": build_ml_engineer_dfa,
    "QA_ENGINEER": build_qa_engineer_dfa,
    "DATA_ANALYST": build_data_analyst_dfa,
}


def build_all() -> Dict[str, DeterministicFiniteAutomaton]:
    return {name: build() for name, build in BUILDERS.items()}


def formal_definition(name: str, dfa: DeterministicFiniteAutomaton) -> str:
    """Devuelve la 5-tupla M = (Q, Σ, δ, q0, F) en Markdown."""
    states = sorted(str(s) for s in dfa.states)
    symbols = sorted(str(s) for s in dfa.symbols)
    q0 = str(next(iter(dfa.start_state)) if isinstance(dfa.start_state, set) else dfa.start_state)
    finals = sorted(str(s) for s in dfa.final_states)
    return "\n".join([
        f"### DFA `{name}`",
        f"- **Q** ({len(states)} estados): {{{', '.join(states)}}}",
        f"- **Σ** ({len(symbols)} símbolos): {{{', '.join(symbols)}}}",
        f"- **q0**: {q0}",
        f"- **F**: {{{', '.join(finals)}}}",
        f"- **δ**: {dfa.get_number_transitions()} transiciones, determinista y parcial "
        f"(sin transición = rechazo). δ(S, t) = S ∪ {{categoría(t)}} si es obligatoria; "
        f"δ(S, t) = S si es opcional.",
        f"- **Determinista**: {dfa.is_deterministic()}",
    ])


def export_dot(dfas: Dict[str, DeterministicFiniteAutomaton], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, dfa in dfas.items():
        dfa.write_as_dot(str(out_dir / f"dfa_{name.lower()}.dot"))


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    automata = build_all()
    export_dot(automata, Path("docs/diagrams/dfa"))
    for n, a in automata.items():
        print(formal_definition(n, a), "\n")
