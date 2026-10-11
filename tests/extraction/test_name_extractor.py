"""Tests de name_extractor.py."""

import pytest

from src.extraction.name_extractor import extract_name


@pytest.mark.parametrize("text,expected", [
    ("Wednesday Addams\n3 years of experience", "Wednesday Addams"),
    ("   John Doe  \nEmail: john@x.com", "John Doe"),
    ("Mary Jane Watson\nTechnical Skills:\nPython", "Mary Jane Watson"),
    ("Johan Mora\nEducación:", "Johan Mora"),
    ("\n\nAna María Pérez-Gómez", "Ana María Pérez-Gómez"),
    ("Technical Skills:\nPython\nJohn Doe", "John Doe"),
    ("María de la Cruz", "María de la Cruz"),
    ("Ludwig van Beethoven", "Ludwig van Beethoven"),
])
def test_extracts_name(text, expected):
    assert extract_name(text) == expected


@pytest.mark.parametrize("text", [
    "",
    "   ",
    None,
    "Technical Skills",
    "Email: john@example.com",
    "Phone: +1-555-0199",
    "3 years of experience",
])
def test_returns_none_when_no_name(text):
    assert extract_name(text) is None
