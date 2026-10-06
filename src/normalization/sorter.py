"""Etapa 2 - Orden canónico según el perfil.

Ordena por categoría (canonical_order) y, dentro de la categoría, por el orden
en que se declaran las opciones. Descarta los tokens que no son del perfil.
Así el resultado no depende del orden en que el candidato escribió su CV.
"""

from typing import Dict, List


def sort_for_profile(skills: List[str], profile: Dict) -> List[str]:
    rank: Dict[str, tuple] = {}
    for cat_idx, category in enumerate(profile["canonical_order"]):
        for opt_idx, token in enumerate(profile["categories"][category]):
            rank[token] = (cat_idx, opt_idx)
    valid = {s for s in skills if s in rank}
    return sorted(valid, key=lambda s: rank[s])