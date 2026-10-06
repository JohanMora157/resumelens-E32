"""Módulo de clasificación de ResumeLens."""

from src.classification.classifier import classify_candidate
from src.classification.profiles import (
    DATA_ANALYST,
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    PROFILES,
    QA_ENGINEER,
)

__all__ = [
    "DATA_ANALYST",
    "FULL_STACK_DEVELOPER",
    "MACHINE_LEARNING_ENGINEER",
    "PROFILES",
    "QA_ENGINEER",
    "classify_candidate",
]