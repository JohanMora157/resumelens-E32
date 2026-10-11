"""Tests de la gramática textX: programas válidos aceptados e inválidos rechazados."""

import pytest

from src.grammar.validator import DSLValidationError, is_valid_dsl, validate_dsl

VALID = '''candidate "Wednesday Addams" {
  contact { email: wednesday@example.com  phone: +1-555-0199 }
  experience { years: 3  description: "web applications" }
  education { "Bachelor's degree", "Computer Science" }
  skills { JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT }
  classification {
    FULL_STACK_DEVELOPER: ACCEPTED
    MACHINE_LEARNING_ENGINEER: REJECTED
  }
}'''


def _program(contact="contact { }", experience="", education="education { }",
             skills="skills { }", classification="classification { }", name='"X"'):
    return f"candidate {name} {{ {contact} {experience} {education} {skills} {classification} }}"


# ---------- válidos ----------

def test_full_valid_profile_is_parsed_into_a_model():
    m = validate_dsl(VALID)
    assert m.name == "Wednesday Addams"
    assert m.contact.email == "wednesday@example.com"
    assert m.contact.phone == "+1-555-0199"
    assert [e.years for e in m.experiences] == [3]
    assert m.education.entries == ["Bachelor's degree", "Computer Science"]
    assert m.skills.names == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert [(r.profile, r.status) for r in m.classification.results] == [
        ("FULL_STACK_DEVELOPER", "ACCEPTED"), ("MACHINE_LEARNING_ENGINEER", "REJECTED")]


def test_minimal_profile_with_empty_blocks_is_valid():
    m = validate_dsl(_program())
    assert m.contact.email is None and m.skills.names == [] and m.experiences == []


def test_repeated_experiences_and_education_entries():
    text = _program(experience="experience { years: 2 } experience { years: 5 description: \"cloud\" }",
                    education='education { "A", "B", "C" }')
    m = validate_dsl(text)
    assert [e.years for e in m.experiences] == [2, 5]
    assert len(m.education.entries) == 3


def test_only_phone_or_only_email_is_valid():
    assert is_valid_dsl(_program(contact="contact { phone: (555) 234-5678 }"))
    assert is_valid_dsl(_program(contact="contact { email: a.b+c@sub.domain.co.uk }"))


def test_comments_are_ignored():
    assert is_valid_dsl("// perfil\n" + _program() + "\n/* fin */")


def test_all_four_profiles_and_both_statuses():
    results = "FULL_STACK_DEVELOPER: ACCEPTED MACHINE_LEARNING_ENGINEER: REJECTED QA_ENGINEER: REJECTED DATA_ANALYST: ACCEPTED"
    assert len(validate_dsl(_program(classification=f"classification {{ {results} }}")).classification.results) == 4


# ---------- inválidos: reglas léxicas ----------

@pytest.mark.parametrize("contact", [
    "contact { email: not-an-email }", "contact { email: user@ }", "contact { email: @domain.com }",
    "contact { phone: abc }", "contact { phone: 12 }",
])
def test_lexical_errors_in_contact_are_rejected(contact):
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(_program(contact=contact))
    assert err.value.kind == "syntax"


@pytest.mark.parametrize("skills", ["skills { react }", "skills { React }", "skills { 1ABC }",
                                    "skills { GIT; REACT }", "skills { GIT REACT }"])
def test_lexical_errors_in_skills_are_rejected(skills):
    assert not is_valid_dsl(_program(skills=skills))


def test_unterminated_string_is_rejected():
    assert not is_valid_dsl('candidate "Sin cerrar { contact { } education { } skills { } classification { } }')


# ---------- inválidos: reglas sintácticas ----------

@pytest.mark.parametrize("text", [
    "", "candidate", "candidate X { }",                        # nombre sin comillas / cuerpo vacío
    'candidate "X" { skills { } classification { } }',          # faltan contact y education
    'candidate "X" { contact { } education { } classification { } skills { } }',   # bloques desordenados
    'candidate "X" { contact { } education { } skills { } classification { }',     # falta la llave final
    'candidate "X" { contact { } education { } skills { } classification { } } extra',
    'candidate "X" { contact { } education { } skills { } classification { CHEF: ACCEPTED } }',
    'candidate "X" { contact { } education { } skills { } classification { QA_ENGINEER: MAYBE } }',
    'candidate "X" { contact { } experience { } education { } skills { } classification { } }',
    'candidate "X" { contact { } experience { years: tres } education { } skills { } classification { } }',
    'candidate "X" { contact { phone: +1-555-0199 email: a@b.co } education { } skills { } classification { } }',
])
def test_syntax_errors_are_rejected(text):
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(text)
    assert err.value.kind == "syntax"


def test_error_message_has_position():
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(_program(skills="skills { react }"))
    assert "1:" in str(err.value)


# ---------- inválidos: reglas semánticas ----------

def test_duplicate_skill_is_rejected():
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(_program(skills="skills { GIT, GIT }"))
    assert err.value.kind == "semantic"


def test_duplicate_profile_in_classification_is_rejected():
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(_program(classification="classification { QA_ENGINEER: ACCEPTED QA_ENGINEER: REJECTED }"))
    assert err.value.kind == "semantic"


@pytest.mark.parametrize("years", [61, 999])
def test_years_out_of_range_is_rejected(years):
    with pytest.raises(DSLValidationError) as err:
        validate_dsl(_program(experience=f"experience {{ years: {years} }}"))
    assert err.value.kind == "semantic"


def test_empty_name_is_rejected():
    with pytest.raises(DSLValidationError):
        validate_dsl(_program(name='"   "'))


def test_is_valid_dsl_returns_booleans():
    assert is_valid_dsl(VALID) is True
    assert is_valid_dsl("basura") is False
