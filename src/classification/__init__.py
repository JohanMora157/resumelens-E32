"""Módulo de clasificación de ResumeLens."""

from src.classification.classifier import classify_candidate
from src.classification.profiles import (
    AI_DATA,
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    SOFTWARE_ENGINEERING,
)

__all__ = [
    "AI_DATA",
    "FULL_STACK_DEVELOPER",
    "MACHINE_LEARNING_ENGINEER",
    "SOFTWARE_ENGINEERING",
    "classify_candidate",
]
