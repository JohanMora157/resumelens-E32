"""Etapa 2 - Construcción de los transductores de estados finitos (FST).

Se construye UN FST por familia tecnológica (LANGUAGES, FRONTEND, ...), leyendo
data/aliases.json. Cada alias es un camino independiente de estados:

    q0 --J/ε--> q1 --S/JAVASCRIPT--> q2 (final)

- Cada transición lee UNA letra (entrada).
- Las letras intermedias emiten ε (lista vacía).
- La última letra emite el token canónico.
- Mayúsculas/minúsculas se resuelven DENTRO del FST (dos transiciones por letra),
  por eso aliases.json solo guarda variantes realmente distintas.
- Cada token canónico también es un alias de sí mismo (NODE_JS -> NODE_JS), para que
  normalizar sea idempotente.

Los caminos NO comparten prefijos: con un trie, "Node" y "NodeJS" emitirían
NODE_JS dos veces. Con caminos separados el FST es no determinista, pero una
palabra solo se acepta si recorre un camino completo.
"""

import json
from pathlib import Path
from typing import Dict, List

from pyformlang.fst import FST

ALIASES_PATH = Path(__file__).resolve().parents[2] / "data" / "aliases.json"


def build_fst(aliases: Dict[str, List[str]]) -> FST:
    """Construye el FST de una familia: {canónico: [alias, ...]}."""
    fst = FST()
    fst.add_start_state("q0")

    seen: Dict[str, str] = {}  # alias en minúscula -> canónico (detecta conflictos)
    n = 0
    for canonical, variants in aliases.items():
        for alias in [canonical, *variants]:  # el canónico se reconoce a sí mismo
            key = alias.lower()
            if key in seen:
                if seen[key] != canonical:
                    raise ValueError(f"Alias '{alias}' ambiguo: {seen[key]} y {canonical}")
                continue  # duplicado solo por mayúsculas: no crear otro camino
            seen[key] = canonical

            prev = "q0"
            for i, ch in enumerate(alias):
                n += 1
                nxt = f"q{n}"
                is_last = i == len(alias) - 1
                output = [canonical] if is_last else []  # ε salvo en la última letra
                for c in {ch.lower(), ch.upper()}:       # insensible a mayúsculas
                    fst.add_transition(prev, c, nxt, output)
                prev = nxt
            fst.add_final_state(prev)
    return fst


def load_fsts(path: Path = ALIASES_PATH) -> Dict[str, FST]:
    """Lee aliases.json y devuelve {familia: FST}."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {family: build_fst(aliases) for family, aliases in data.items()}