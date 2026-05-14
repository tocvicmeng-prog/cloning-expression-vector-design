"""
module_id: tests.domain.sequence
file: tests/domain/sequence/test_feature_qualifier.py
task_id: T-301
"""

from __future__ import annotations

import pytest

from domain.sequence import FeatureV14, InsertionContext, LocationV14, Qualifier


def test_qualifier_preserves_type_and_order() -> None:
    qualifier = Qualifier(
        namespace="GenBank",
        key="gene",
        value="lacZ",
        value_type="string",
        order=2,
        provenance="fixture",
    )

    assert qualifier.value == "lacZ"
    assert qualifier.order == 2


def test_qualifier_rejects_mismatched_type() -> None:
    with pytest.raises(TypeError, match="does not match"):
        Qualifier(namespace="GenBank", key="pseudo", value="true", value_type="boolean", order=0)


def test_qualifier_validates_scalar_types_and_required_fields() -> None:
    assert Qualifier(namespace="GenBank", key="pseudo", value=True, value_type="boolean", order=0)
    assert Qualifier(namespace="GenBank", key="rank", value=1, value_type="integer", order=1)
    assert Qualifier(namespace="GenBank", key="score", value=1.5, value_type="float", order=2)
    assert Qualifier(
        namespace="SnapGene",
        key="style",
        value=(("color", "blue"),),
        value_type="structured",
        order=3,
    )

    with pytest.raises(ValueError, match="namespace"):
        Qualifier(namespace="", key="gene", value="x", value_type="string", order=0)
    with pytest.raises(ValueError, match="key"):
        Qualifier(namespace="GenBank", key="", value="x", value_type="string", order=0)
    with pytest.raises(ValueError, match="order"):
        Qualifier(namespace="GenBank", key="gene", value="x", value_type="string", order=-1)


def test_feature_sorts_qualifiers_without_losing_duplicates() -> None:
    location = LocationV14(start=0, end=3, strand="+", phase=0)
    second = Qualifier(namespace="GenBank", key="note", value="b", value_type="string", order=2)
    first = Qualifier(namespace="GenBank", key="note", value="a", value_type="string", order=1)
    feature = FeatureV14(
        role="SO:0000316",
        qualifiers=(second, first),
        locations=(location,),
        parent_sequence_id="seq-1",
    )

    assert feature.ordered_qualifiers == (first, second)


def test_feature_requires_location() -> None:
    with pytest.raises(ValueError, match="location"):
        FeatureV14(role="SO:0000316", qualifiers=(), locations=(), parent_sequence_id="seq-1")


def test_feature_requires_role_and_parent_sequence_id() -> None:
    location = LocationV14(start=0, end=3, strand="+", phase=0)

    with pytest.raises(ValueError, match="role"):
        FeatureV14(role="", qualifiers=(), locations=(location,), parent_sequence_id="seq-1")
    with pytest.raises(ValueError, match="parent_sequence_id"):
        FeatureV14(role="SO:0000316", qualifiers=(), locations=(location,), parent_sequence_id="")


def test_insertion_context_validates_phase_effect() -> None:
    with pytest.raises(ValueError, match="phase_effect"):
        InsertionContext(
            parent_node_id="node-1",
            orientation="forward",
            junction_sequence="ACGT",
            scar=None,
            phase_effect=3,
            accepted_overhang_or_overlap=None,
            insertion_point=LocationV14(start=0, end=1, strand="+", phase="."),
        )


def test_insertion_context_requires_parent_node_id() -> None:
    with pytest.raises(ValueError, match="parent_node_id"):
        InsertionContext(
            parent_node_id="",
            orientation="forward",
            junction_sequence="ACGT",
            scar=None,
            phase_effect=0,
            accepted_overhang_or_overlap=None,
            insertion_point=LocationV14(start=0, end=1, strand="+", phase="."),
        )
