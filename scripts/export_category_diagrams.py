"""Diagramas legibles de los DFA: una vista a nivel de CATEGORIA.

El DFA real tiene una transicion por cada skill (hasta 832), lo que no cabe en una imagen.
Aqui cada estado es el subconjunto de categorias obligatorias ya cubiertas y cada flecha
es una CATEGORIA (todas las skills de esa categoria hacen la misma transicion).
Los self-loops (categoria ya cubierta, categoria opcional, skill repetida) se omiten
y se explican en la leyenda.

Uso (desde la raiz):  python -m scripts.export_category_diagrams
"""
import subprocess
from itertools import combinations
from pathlib import Path

from src.classification.profiles import PROFILES
from src.classification.profile_dfa import mandatory_categories

OPTIONAL = {"FULL_STACK_DEVELOPER": ("API",), "DATA_ANALYST": ("SPREADSHEET",)}
PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
OUT = Path("docs/diagrams")


def build_dot(name: str) -> str:
    optional = OPTIONAL.get(name, ())
    cats = mandatory_categories(PROFILES[name], optional)
    color = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cats)}
    k = len(cats)
    ident = lambda s: "s" + "".join("1" if c in s else "0" for c in cats)
    lines = [
        "digraph G {", "  rankdir=LR; splines=true; nodesep=0.25; ranksep=1.1;",
        '  node [shape=circle, width=0.35, fixedsize=true, label="", style=filled, fillcolor="#f1f5f9", color="#64748b"];',
        "  edge [arrowsize=0.6, penwidth=1.2];",
        '  start [shape=point, width=0.1]; start -> s' + "0" * k + ";",
    ]
    for size in range(k + 1):
        members = []
        for subset in combinations(cats, size):
            s = frozenset(subset)
            attrs = ""
            if size == 0:
                attrs = ' [fillcolor="#e2e8f0"]'
            if size == k:
                attrs = ' [shape=doublecircle, fillcolor="#bbf7d0", color="#166534"]'
            lines.append(f"  {ident(s)}{attrs};")
            members.append(ident(s))
        lines.append("  { rank=same; " + "; ".join(members) + "; }")
    for size in range(k):
        for subset in combinations(cats, size):
            s = frozenset(subset)
            for c in cats:
                if c not in s:
                    lines.append(f'  {ident(s)} -> {ident(s | {c})} [color="{color[c]}"];')
    lines.append("  subgraph cluster_leg { label=\"Categorias (color de la flecha)\"; fontsize=12; color=\"#cbd5e1\";")
    for i, c in enumerate(cats):
        lines.append(f'    leg{i} [shape=box, style=filled, fillcolor="{color[c]}", fontcolor=white, '
                     f'width=1.9, height=0.25, fixedsize=true, fontsize=10, label="{c}"];')
    lines.append("  }")
    opt = ", ".join(optional) if optional else "ninguna"
    title = (f"{name}: {2**k} estados (subconjuntos de {k} categorias obligatorias)\\n"
             f"Doble circulo = aceptacion (todas cubiertas). Categorias opcionales: {opt} (self-loop).")
    lines.append(f'  labelloc=t; fontsize=14; label="{title}";')
    lines.append("}")
    return "\n".join(lines)


def build_example_dot() -> str:
    """Ejemplo ilustrativo de 3 categorias, con el contenido de cada estado a la vista."""
    cats = ["LANGUAGE", "DATABASE", "VERSION_CONTROL"]
    short = {"LANGUAGE": "L", "DATABASE": "D", "VERSION_CONTROL": "V"}
    color = {c: PALETTE[i] for i, c in enumerate(cats)}
    k = len(cats)
    ident = lambda s: "s" + "".join("1" if c in s else "0" for c in cats)
    label = lambda s: "{" + ",".join(short[c] for c in cats if c in s) + "}" if s else "\u2205"
    lines = ["digraph G {", "  rankdir=LR; nodesep=0.5; ranksep=1.3;",
             '  node [shape=circle, style=filled, fillcolor="#f1f5f9", color="#64748b", fontsize=12];',
             "  edge [fontsize=11, penwidth=1.6];",
             "  start [shape=point, width=0.1]; start -> s" + "0" * k + ";"]
    for size in range(k + 1):
        for subset in combinations(cats, size):
            s = frozenset(subset)
            extra = ', shape=doublecircle, fillcolor="#bbf7d0", color="#166534"' if size == k else ""
            lines.append(f'  {ident(s)} [label="{label(s)}"{extra}];')
    for size in range(k):
        for subset in combinations(cats, size):
            s = frozenset(subset)
            for c in cats:
                if c not in s:
                    lines.append(f'  {ident(s)} -> {ident(s | {c})} [label="{short[c]}", color="{color[c]}", fontcolor="{color[c]}"];')
    lines.append('  labelloc=t; fontsize=14; label="Ejemplo con 3 categorias: L=LANGUAGE, D=DATABASE, V=VERSION_CONTROL\\n'
                 'Cada estado = categorias ya cubiertas. Los DFA reales tienen 2^k estados (k = categorias obligatorias)."; }')
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in PROFILES:
        dot = OUT / f"dfa_{name.lower()}_categories.dot"
        dot.write_text(build_dot(name), encoding="utf-8")
        subprocess.run(["dot", "-Tpng", "-Gdpi=130", str(dot), "-o", str(dot.with_suffix(".png"))], check=True)
        print("OK", dot.with_suffix(".png"))
    ex = OUT / "dfa_example_3_categories.dot"
    ex.write_text(build_example_dot(), encoding="utf-8")
    subprocess.run(["dot", "-Tpng", "-Gdpi=130", str(ex), "-o", str(ex.with_suffix(".png"))], check=True)
    print("OK", ex.with_suffix(".png"))


if __name__ == "__main__":
    main()
