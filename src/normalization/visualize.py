"""Formalización (7-tupla) y diagramas de los FST, para docs/03_formalization.md.

Uso:  python -m src.normalization.visualize
Luego convertir:  dot -Tpng docs/diagrams/fst/fst_frontend.dot -o docs/diagrams/fst/fst_frontend.png
"""

from pathlib import Path
from typing import Dict

from pyformlang.fst import FST

from src.normalization.transducers import load_fsts


def _num(state) -> int:
    return int(str(state)[1:])


def formal_definition(name: str, fst: FST) -> str:
    """Devuelve la 7-tupla M = (Q, Σ, Γ, δ, ω, q0, F) en Markdown."""
    states = sorted(map(str, fst.states), key=_num)
    q0 = sorted(map(str, fst.start_states))[0]
    finals = sorted(map(str, fst.final_states), key=_num)
    lines = [
        f"### FST `{name}`",
        f"- **Q** ({len(states)} estados): {{{', '.join(states)}}}",
        f"- **Σ** ({len(fst.input_symbols)} símbolos): {{{', '.join(sorted(map(str, fst.input_symbols)))}}}",
        f"- **Γ**: {{ε, {', '.join(sorted(map(str, fst.output_symbols)))}}}",
        f"- **q0**: {q0}",
        f"- **F**: {{{', '.join(finals)}}}",
        "- **δ y ω**: δ(estado, letra) = destino, ω = salida",
    ]
    for (src, symbol), dests in fst.transitions.items():
        for dst, out in dests:
            lines.append(f"  - δ({src}, {symbol}) = {dst}, ω = {''.join(map(str, out)) or 'ε'}")
    return "\n".join(lines)


def export_dot(fsts: Dict[str, FST], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fst in fsts.items():
        fst.write_as_dot(str(out_dir / f"fst_{name.lower()}.dot"))


if __name__ == "__main__":
    fsts = load_fsts()
    export_dot(fsts, Path("docs/diagrams/fst"))
    for fam, f in fsts.items():
        print(formal_definition(fam, f), "\n")