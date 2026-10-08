"""Módulo de clasificación de ResumeLens (Etapa 3: autómatas finitos con pyformlang)."""

from src.classification.classifier import (
    ACCEPTED,
    REJECTED,
    accepted_profiles,
    classify_candidate,
    classify_profile,
)
from src.classification.profiles import (
    DATA_ANALYST,
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    PROFILES,
    QA_ENGINEER,
)

__all__ = [
    "ACCEPTED", "REJECTED",
    "DATA_ANALYST", "FULL_STACK_DEVELOPER", "MACHINE_LEARNING_ENGINEER", "PROFILES", "QA_ENGINEER",
    "accepted_profiles", "classify_candidate", "classify_profile",
]