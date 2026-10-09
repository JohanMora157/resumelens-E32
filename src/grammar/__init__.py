"""Módulo de la gramática de ResumeLens (Etapa 4: DSL del perfil con textX)."""

from src.grammar.builder import build_dsl
from src.grammar.renderer import render_html, render_markdown

try:
    from src.grammar.validator import DSLValidationError, is_valid_dsl, validate_dsl
except ImportError:
    pass

__all__ = [
    name
    for name in [
        "DSLValidationError",
        "build_dsl",
        "is_valid_dsl",
        "render_html",
        "render_markdown",
        "validate_dsl",
    ]
    if name in globals()
]