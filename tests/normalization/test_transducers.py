"""Tests de la construcción de los FST (transducers.py): el objeto formal."""

import json

import pytest

from src.normalization.transducers import ALIASES_PATH, build_fst, load_fsts


def _canonical_vocabulary():
    data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    return {c for family in data.values() for c in family}


def test_one_fst_per_family_in_aliases_json():
    data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    assert set(load_fsts()) == set(data)


def test_fst_has_seven_tuple_components():
    for name, fst in load_fsts().items():
        assert fst.states, name
        assert fst.input_symbols, name
        assert fst.output_symbols, name
        assert len(fst.start_states) == 1, name
        assert fst.final_states, name


def test_final_states_are_subset_of_states():
    for fst in load_fsts().values():
        assert set(fst.final_states) <= set(fst.states)
        assert set(fst.start_states) <= set(fst.states)


def test_output_alphabet_is_canonical_vocabulary():
    vocabulary = _canonical_vocabulary()
    for name, fst in load_fsts().items():
        assert {str(s) for s in fst.output_symbols} <= vocabulary, name


def test_input_alphabet_is_single_characters():
    for name, fst in load_fsts().items():
        assert all(len(str(s)) == 1 for s in fst.input_symbols), name


def test_case_only_duplicates_do_not_add_paths():
    base = build_fst({"A": ["Foo"]})
    dup = build_fst({"A": ["Foo", "FOO", "foo"]})
    assert base.get_number_transitions() == dup.get_number_transitions()
    assert len(base.states) == len(dup.states)


def test_ambiguous_alias_in_same_family_raises():
    with pytest.raises(ValueError):
        build_fst({"A": ["x"], "B": ["X"]})


def test_alias_equal_to_other_canonical_raises():
    with pytest.raises(ValueError):
        build_fst({"A": ["b"], "B": ["z"]})


def test_translate_returns_canonical_for_alias_and_nothing_otherwise():
    fst = build_fst({"JAVASCRIPT": ["JS", "Javascript"]})
    assert [str(x) for x in list(fst.translate(list("js")))[0]] == ["JAVASCRIPT"]
    assert list(fst.translate(list("jsx"))) == []
    assert list(fst.translate(list("j"))) == []


def test_prefix_alias_emits_output_once():
    """Node y NodeJS comparten prefijo: cada palabra emite UN solo token."""
    fst = build_fst({"NODE_JS": ["Node", "NodeJS"]})
    for word in ("Node", "NodeJS"):
        outputs = list(fst.translate(list(word)))
        assert outputs and all(len(o) == 1 for o in outputs)