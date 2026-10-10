"""Módulo de procesamiento y validación sintáctica mediante gramáticas libres de contexto (textX)."""

from pathlib import Path
from typing import Any, Dict, Union

from src.grammar.builder import build_dsl
from src.grammar.validator import GRAMMAR_PATH, DSLValidationError, validate_dsl


def parse_candidate_profile(
    data: Union[str, Dict[str, Any]],
    grammar_path: Path = GRAMMAR_PATH,
) -> Any:
    """Valida y estructura la información del perfil del candidato según la gramática libre de contexto.

    Acepta tanto un texto en formato DSL como un diccionario con los datos estructurados
    del candidato. Si recibe un diccionario, construye el programa DSL correspondiente
    mediante el builder y posteriormente lo valida con textX.

    Args:
        data (Union[str, Dict[str, Any]]): Texto en DSL o diccionario con los campos del candidato.
        grammar_path (Path): Ruta al archivo de gramática resume.tx.

    Returns:
        Any: Modelo semántico validado del candidato según la gramática libre de contexto.

    Raises:
        DSLValidationError: Si el perfil contiene errores sintácticos o viola reglas semánticas.
        TypeError: Si el parámetro data no es una cadena de texto ni un diccionario.
    """
    if isinstance(data, str):
        dsl_text = data
    elif isinstance(data, dict):
        contact = data.get("contact", {})
        email = data.get("email") or (contact.get("email") if isinstance(contact, dict) else None)
        phone = data.get("phone") or (contact.get("phone") if isinstance(contact, dict) else None)

        dsl_text = build_dsl(
            name=data.get("name", "Unknown Candidate"),
            email=email,
            phone=phone,
            experience=data.get("experience", []),
            education=data.get("education", []),
            skills=data.get("skills", []) or data.get("canonical_skills", []),
            classification=data.get("classification", {}),
        )
    else:
        raise TypeError(
            f"Tipo de dato no soportado para el perfil del candidato: {type(data).__name__}"
        )

    return validate_dsl(dsl_text, grammar_path=grammar_path)
