"""Módulo de la gramática de ResumeLens (Etapa 4: DSL del perfil con textX)."""

from src.grammar.builder import build_dsl
from src.grammar.renderer import render_html, render_markdown
from src.grammar.validator import DSLValidationError, is_valid_dsl, validate_dsl

__all__ = ["DSLValidationError", "build_dsl", "is_valid_dsl",
           "render_html", "render_markdown", "validate_dsl"]