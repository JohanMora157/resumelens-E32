"""Pipeline de ResumeLens: SOLO orquesta las 4 etapas (no contiene lógica propia).

  texto del CV
    -> Etapa 1  extract_resume_information (regex)
    -> Etapa 2  normalize (FST) + sort_for_profile
    -> Etapa 3  classify_candidate (autómatas)
    -> Etapa 4  build_dsl -> validate_dsl (textX) -> render_html / render_markdown
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.classification.classifier import classify_candidate
from src.classification.profiles import PROFILES
from src.extraction.name_extractor import extract_name
from src.extraction.regex_extractor import extract_resume_information
from src.grammar.builder import build_dsl
from src.grammar.renderer import render_html, render_markdown
from src.grammar.validator import DSLValidationError, validate_dsl
from src.normalization.normalizer import normalize
from src.normalization.sorter import sort_for_profile


@dataclass
class PipelineResult:
    name: str = "Unknown Candidate"
    extracted: Dict[str, Any] = field(default_factory=dict)
    canonical_skills: List[str] = field(default_factory=list)
    unknown_skills: List[str] = field(default_factory=list)
    sorted_by_profile: Dict[str, List[str]] = field(default_factory=dict)
    classification: Dict[str, str] = field(default_factory=dict)
    dsl_text: str = ""
    model: Any = None
    html: Optional[str] = None
    markdown: Optional[str] = None
    error: Optional[str] = None


def run_pipeline(text: str) -> PipelineResult:
    result = PipelineResult()

    # Etapa 1: regex
    result.extracted = extract_resume_information(text)
    result.name = extract_name(text) or result.name

    # Etapa 2: FST + orden por perfil
    result.canonical_skills, result.unknown_skills = normalize(result.extracted["technical_skills"])
    result.sorted_by_profile = {
        name: sort_for_profile(result.canonical_skills, profile) for name, profile in PROFILES.items()}

    # Etapa 3: autómatas
    result.classification = classify_candidate(result.canonical_skills)

    # Etapa 4: DSL -> textX -> visualización
    contact = result.extracted["contact"]
    result.dsl_text = build_dsl(
        name=result.name, email=contact["email"], phone=contact["phone"],
        experience=result.extracted["experience"], education=result.extracted["education"],
        skills=result.canonical_skills, classification=result.classification)
    try:
        result.model = validate_dsl(result.dsl_text)
        result.html = render_html(result.model)
        result.markdown = render_markdown(result.model)
    except DSLValidationError as error:
        result.error = str(error)
    return result


def process_resume(resume_text: str) -> PipelineResult:
    """Función de compatibilidad con la firma original del pipeline."""
    return run_pipeline(resume_text)


def extract_candidate_name(text: Optional[str]) -> str:
    """Extrae el nombre del candidato o devuelve 'Unknown Candidate'."""
    return extract_name(text) or "Unknown Candidate"
