"""Stage 4 - DSL validation using textX.

validate_dsl(text) loads the resume.tx grammar on demand and returns
a Python model when valid.

It rejects:
- Lexical and syntactic violations defined by textX.
- Semantic violations not expressible by the context-free grammar:
  empty candidate name, experience years out of range (0-60), duplicate skills,
  and duplicate classification profiles.

Validation failures are represented by DSLValidationError.
"""

import functools
from pathlib import Path
from typing import Optional

from textx import metamodel_from_file
from textx.exceptions import TextXError, TextXSemanticError

GRAMMAR_PATH = Path(__file__).resolve().parent / "resume.tx"
MAX_YEARS = 60


class DSLValidationError(ValueError):
    """Raised when a DSL candidate profile is invalid."""

    def __init__(
        self,
        message: str,
        kind: str = "syntax",
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        super().__init__(message)
        self.kind = kind
        self.line = line
        self.col = col


def _check_candidate(candidate):
    """Semantic check: reject empty or whitespace-only candidate name."""
    name = getattr(candidate, "name", "")
    if not name or not name.strip():
        raise TextXSemanticError(
            "El nombre del candidato no puede estar vacío."
        )


def _check_experience(experience):
    """Semantic check: experience years must satisfy 0 <= years <= MAX_YEARS."""
    years = getattr(experience, "years", None)
    if years is None or not (0 <= years <= MAX_YEARS):
        raise TextXSemanticError(
            f"Años de experiencia fuera de rango (0-{MAX_YEARS}): "
            f"{years}"
        )


def _check_skills(skills):
    """Semantic check: reject duplicate skill identifiers."""
    seen = set()
    names = getattr(skills, "names", [])
    for name in names:
        if name in seen:
            raise TextXSemanticError(f"Skill repetida: {name}")
        seen.add(name)


def _check_classification(classification):
    """Semantic check: reject duplicate classification profiles."""
    seen = set()
    results = getattr(classification, "results", [])
    for result in results:
        profile = getattr(result, "profile", None)
        if profile in seen:
            raise TextXSemanticError(
                f"Perfil repetido en la clasificación: {profile}"
            )
        seen.add(profile)


@functools.lru_cache(maxsize=None)
def _get_metamodel(grammar_path: Path = GRAMMAR_PATH):
    """Lazy loader for the textX metamodel.

    Loads the metamodel and registers object processors only when requested.
    Raises DSLValidationError with kind='configuration' if the grammar file does not exist.
    """
    grammar_file = Path(grammar_path)
    if not grammar_file.exists():
        raise DSLValidationError(
            f"El archivo de gramática no existe: {grammar_file}",
            kind="configuration",
        )

    metamodel = metamodel_from_file(str(grammar_file))
    metamodel.register_obj_processors({
        "Candidate": _check_candidate,
        "Experience": _check_experience,
        "Skills": _check_skills,
        "Classification": _check_classification,
    })
    return metamodel


def validate_dsl(text: str, grammar_path: Path = GRAMMAR_PATH):
    """Return the validated textX model or raise DSLValidationError.

    Raises:
        DSLValidationError(kind='configuration'): if resume.tx grammar file is missing.
        DSLValidationError(kind='semantic'): if a semantic rule is violated.
        DSLValidationError(kind='syntax'): if lexical or syntactic syntax error occurs.
    """
    metamodel = _get_metamodel(grammar_path)
    try:
        return metamodel.model_from_str(text)
    except TextXSemanticError as error:
        raise DSLValidationError(
            str(error),
            kind="semantic",
            line=getattr(error, "line", None),
            col=getattr(error, "col", None),
        ) from error
    except TextXError as error:
        raise DSLValidationError(
            str(error),
            kind="syntax",
            line=getattr(error, "line", None),
            col=getattr(error, "col", None),
        ) from error


def is_valid_dsl(text: str, grammar_path: Path = GRAMMAR_PATH) -> bool:
    """Return True if DSL text is valid, False if invalid.

    Note:
        Propagates configuration errors (e.g. missing grammar file)
        instead of returning False, to distinguish system configuration issues
        from invalid user DSL input.
    """
    try:
        validate_dsl(text, grammar_path)
        return True
    except DSLValidationError as error:
        if error.kind == "configuration":
            raise
        return False
