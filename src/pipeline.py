"""ResumeLens - Pipeline.

Módulo de orquestación del pipeline integral de procesamiento y clasificación de hojas de vida.

Flujo formal:
1. Regex extraction (src.extraction.regex_extractor): Extracción de texto relevante, contacto,
   experiencia, educación y tokens de cualificaciones.
2. FST normalization (src.normalization.normalizer): Mapeo determinista de cualificaciones
   hacia nombres canónicos mediante transductores de estados finitos.
3. Canonical ordering (src.normalization.sorter): Ordenamiento canónico de cualificaciones según
   cada uno de los perfiles profesionales formales.
4. Finite automata classification (src.classification.classifier): Reconocimiento y clasificación
   de patrones mediante autómatas finitos deterministas (ACCEPTED / REJECTED).
5. CFG DSL construction & validation (src.grammar.builder / src.grammar.validator): Construcción
   del programa de perfil en el DSL de textX y validación sintáctica/semántica.
6. Visualization rendering (src.grammar.renderer): Generación de representaciones HTML y Markdown.
"""

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional

from src.classification.classifier import classify_candidate
from src.classification.profiles import PROFILES
from src.extraction.regex_extractor import extract_resume_information
from src.grammar.builder import build_dsl
from src.grammar.renderer import render_html, render_markdown
from src.grammar.validator import DSLValidationError, validate_dsl
from src.normalization.normalizer import normalize
from src.normalization.sorter import sort_for_profile

_SECTION_HEADERS = {
    "technical skills", "skills", "technologies", "programming languages",
    "frameworks", "databases", "tools", "tech stack", "habilidades",
    "tecnologias", "tecnologías", "educacion", "educación", "education",
    "formacion", "formación", "academic", "experiencia", "experience",
    "work experience", "professional experience", "proyectos", "projects",
    "certificaciones", "certifications", "contacto", "contact",
    "resumen", "summary", "perfil", "profile", "references", "referencias",
}


def extract_candidate_name(text: str) -> str:
    """Extrae el nombre del candidato a partir del texto de la hoja de vida.

    Generalmente es la primera línea no vacía que no corresponde a un encabezado de sección
    ni a información de contacto.

    Args:
        text (str): Texto plano del currículum.

    Returns:
        str: Nombre inferido del candidato o 'Unknown Candidate' como valor por defecto.
    """
    if not text or not text.strip():
        return "Unknown Candidate"

    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        cleaned = re.sub(r"^[#*•\-\s]+", "", line).strip()
        cleaned_no_punct = cleaned.rstrip(":").strip()
        if cleaned_no_punct.lower() in _SECTION_HEADERS:
            continue
        if "@" in cleaned or re.search(
            r"\b(?:email|correo|phone|tel|teléfono|celular|mobile)\b", cleaned, re.IGNORECASE
        ):
            continue
        if re.search(r"^\+?\d[\d\s\-\.\(\)]{6,}\b", cleaned):
            continue
        candidate_name = cleaned.strip("\"' ")
        if candidate_name:
            return candidate_name

    return "Unknown Candidate"


@dataclass
class PipelineResult:
    """Resultado estructurado de la ejecución del pipeline formal de ResumeLens.

    Attributes:
        name: Nombre del candidato extraído.
        extracted: Diccionario de datos extraídos por expresiones regulares (contacto,
            experiencia, educación, technical_skills).
        canonical_skills: Lista de habilidades normalizadas mediante FST.
        unknown_skills: Lista de habilidades que no fueron reconocidas por ningún FST.
        sorted_by_profile: Diccionario con la ordenación canónica de habilidades para cada perfil.
        classification: Diccionario con el veredicto DFA ('ACCEPTED' o 'REJECTED') por perfil.
        dsl_text: Representación textual generada según el DSL formal de textX.
        model: Objeto del metamodelo textX validado (None si falló la validación o falta la gramática).
        validation_error: Error capturado durante la validación sintáctica/semántica, si lo hubo.
        html: Visualización generada en formato HTML.
        markdown: Visualización generada en formato Markdown.
    """

    name: str
    extracted: Dict[str, Any]
    canonical_skills: List[str]
    unknown_skills: List[str]
    sorted_by_profile: Dict[str, List[str]]
    classification: Dict[str, str]
    dsl_text: str
    model: Optional[Any] = None
    validation_error: Optional[Any] = None
    html: Optional[str] = None
    markdown: Optional[str] = None


def run_pipeline(resume_text: str) -> PipelineResult:
    """Ejecuta el pipeline completo de ResumeLens para una hoja de vida.

    Etapas ejecutadas:
    1. Extracción de información mediante expresiones regulares (nombre, contacto,
       experiencia, educación, skills crudas).
    2. Normalización de skills con FST (transductores de estados finitos).
    3. Ordenamiento canónico de skills por categoría para cada uno de los 4 perfiles.
    4. Clasificación formal de candidatos con autómatas finitos deterministas (DFA).
    5. Construcción y validación del DSL con gramática libre de contexto (textX).
    6. Renderizado de fichas en HTML y Markdown.

    Args:
        resume_text (str): Texto sin formato del currículum a evaluar.

    Returns:
        PipelineResult: Contenedor con todos los artefactos y resultados del análisis.
    """
    # 1. Extracción con expresiones regulares
    name = extract_candidate_name(resume_text)
    extracted = extract_resume_information(resume_text)
    raw_skills = extracted.get("technical_skills", [])
    contact = extracted.get("contact", {})
    experience = extracted.get("experience", [])
    education = extracted.get("education", [])

    # 2. Normalización con transductores finitos (FST)
    canonical_skills, unknown_skills = normalize(raw_skills)

    # 3. Ordenamiento canónico por perfil
    sorted_by_profile: Dict[str, List[str]] = {}
    for profile_name, profile_data in PROFILES.items():
        sorted_by_profile[profile_name] = sort_for_profile(canonical_skills, profile_data)

    # 4. Clasificación con autómatas finitos (DFA)
    classification = classify_candidate(canonical_skills)

    # 5. Generación del DSL
    dsl_text = build_dsl(
        name=name,
        email=contact.get("email"),
        phone=contact.get("phone"),
        experience=experience,
        education=education,
        skills=canonical_skills,
        classification=classification,
    )

    # 6. Validación con textX y renderizado visual
    model = None
    validation_error = None
    html = None
    markdown = None

    try:
        model = validate_dsl(dsl_text)
        html = render_html(model)
        markdown = render_markdown(model)
    except (DSLValidationError, Exception) as exc:
        validation_error = exc

    return PipelineResult(
        name=name,
        extracted=extracted,
        canonical_skills=canonical_skills,
        unknown_skills=unknown_skills,
        sorted_by_profile=sorted_by_profile,
        classification=classification,
        dsl_text=dsl_text,
        model=model,
        validation_error=validation_error,
        html=html,
        markdown=markdown,
    )


def process_resume(resume_text: str) -> PipelineResult:
    """Función de conveniencia compatible con la firma original del pipeline.

    Args:
        resume_text (str): Texto plano del CV a evaluar.

    Returns:
        PipelineResult: Resultado del procesamiento del perfil del candidato.
    """
    return run_pipeline(resume_text)
