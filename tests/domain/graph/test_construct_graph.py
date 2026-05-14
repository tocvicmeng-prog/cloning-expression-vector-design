"""
module_id: tests.domain.graph
file: tests/domain/graph/test_construct_graph.py
task_id: T-302
"""

from __future__ import annotations

from copy import deepcopy
from typing import cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from domain.graph import (
    ConstructGraph,
    Edge,
    EdgeKind,
    GraphNode,
    GraphNodeKind,
    NodeId,
    derive_feature_table,
)
from domain.sequence import (
    CompoundLocationKind,
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
    Topology,
)


def _record(topology: Topology = "linear") -> SequenceRecord:
    return SequenceRecord(
        id="seq-1",
        sequence=DnaSequence("ACGTACGT"),
        topology=topology,
        molecule_type=MoleculeType.DS_DNA,
    )


def _feature(name: str, start: int = 0, end: int = 3) -> FeatureV14:
    return FeatureV14(
        role="SO:0000316",
        qualifiers=(
            Qualifier(
                namespace="GenBank",
                key="gene",
                value=name,
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=start, end=end, strand="+", phase=0),),
        parent_sequence_id="seq-1",
    )


def _part_node(node_id: str) -> GraphNode:
    return GraphNode(id=NodeId(node_id), kind="part", payload=(("part_id", node_id),))


def _round_trip_graph() -> ConstructGraph:
    return ConstructGraph(
        nodes=(
            _part_node("part-1"),
            GraphNode(id=NodeId("feature-a"), kind="feature", payload=_feature("gene")),
        ),
        edges=(
            Edge(
                source=NodeId("part-1"),
                target=NodeId("feature-a"),
                kind=EdgeKind.DERIVATION,
                annotations=(("source", "fixture"),),
            ),
        ),
        topology="linear",
        sequence_record=_record(),
    )


def test_graph_validates_edge_endpoints() -> None:
    with pytest.raises(ValueError, match="source"):
        ConstructGraph(
            nodes=(_part_node("part-1"),),
            edges=(
                Edge(
                    source=NodeId("missing"),
                    target=NodeId("part-1"),
                    kind=EdgeKind.ADJACENCY,
                ),
            ),
            topology="linear",
            sequence_record=_record(),
        )

    with pytest.raises(ValueError, match="target"):
        ConstructGraph(
            nodes=(_part_node("part-1"),),
            edges=(
                Edge(
                    source=NodeId("part-1"),
                    target=NodeId("missing"),
                    kind=EdgeKind.ADJACENCY,
                ),
            ),
            topology="linear",
            sequence_record=_record(),
        )


def test_graph_requires_nodes_and_known_topology() -> None:
    with pytest.raises(ValueError, match="at least one node"):
        ConstructGraph(nodes=(), edges=(), topology="linear", sequence_record=_record())

    with pytest.raises(ValueError, match="linear or circular"):
        ConstructGraph(
            nodes=(_part_node("part-1"),),
            edges=(),
            topology=cast(Topology, "plasmid"),
            sequence_record=_record(),
        )


def test_graph_topology_must_match_sequence_record() -> None:
    with pytest.raises(ValueError, match="topology"):
        ConstructGraph(
            nodes=(_part_node("part-1"),),
            edges=(),
            topology="circular",
            sequence_record=_record("linear"),
        )


def test_node_map_returns_nodes_by_id() -> None:
    graph = ConstructGraph(
        nodes=(_part_node("part-1"),),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )

    assert graph.node_map[NodeId("part-1")].payload == (("part_id", "part-1"),)


def test_duplicate_node_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        ConstructGraph(
            nodes=(_part_node("part-1"), _part_node("part-1")),
            edges=(),
            topology="linear",
            sequence_record=_record(),
        )


def test_feature_table_is_derived_from_feature_nodes_in_canonical_order() -> None:
    second_feature = _feature("second", start=4, end=7)
    first_feature = _feature("first", start=0, end=3)
    graph = ConstructGraph(
        nodes=(
            GraphNode(id=NodeId("feature-b"), kind="feature", payload=second_feature),
            _part_node("part-1"),
            GraphNode(id=NodeId("feature-a"), kind="feature", payload=first_feature),
        ),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )

    assert graph.feature_table == (first_feature, second_feature)
    assert graph.feature_table == derive_feature_table(graph)


def test_state_transition_methods_preserve_derived_feature_table() -> None:
    feature_node = GraphNode(id=NodeId("feature-a"), kind="feature", payload=_feature("gene"))
    graph = ConstructGraph(
        nodes=(_part_node("part-1"),),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    ).with_node(feature_node)
    graph = graph.with_edge(
        Edge(source=NodeId("part-1"), target=NodeId("feature-a"), kind=EdgeKind.DERIVATION),
    )

    assert graph.feature_table == derive_feature_table(graph)


def test_graph_round_trips_through_canonical_json() -> None:
    graph = _round_trip_graph()

    restored = ConstructGraph.from_canonical_json(graph.canonical_json())

    assert restored == graph
    assert restored.canonical_json() == graph.canonical_json()


def test_graph_round_trips_text_payload_structured_qualifier_and_compound_location() -> None:
    child = LocationV14(start=0, end=3, strand="+", phase=".")
    second_child = LocationV14(start=4, end=7, strand="+", phase=".")
    feature = FeatureV14(
        role="SO:0000316",
        qualifiers=(
            Qualifier(
                namespace="SnapGene",
                key="style",
                value=(("color", "blue"),),
                value_type="structured",
                order=0,
                provenance="fixture",
            ),
        ),
        locations=(
            LocationV14(
                start=0,
                end=7,
                strand="+",
                phase=".",
                sub_locations=(child, second_child),
                sub_kind=CompoundLocationKind.JOIN,
                complement_compound=True,
                remote_accession="REMOTE1",
                partial_at_5p=True,
                partial_at_3p=True,
            ),
        ),
        parent_sequence_id="seq-1",
        evidence=("PMID:1",),
        sub_features=(_feature("child"),),
    )
    graph = ConstructGraph(
        nodes=(
            GraphNode(id=NodeId("module-a"), kind="module", payload="module-token"),
            GraphNode(id=NodeId("feature-a"), kind="feature", payload=feature),
        ),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )

    assert ConstructGraph.from_canonical_json(graph.canonical_json()) == graph


def test_feature_nodes_require_feature_payloads() -> None:
    with pytest.raises(TypeError, match="FeatureV14"):
        GraphNode(id=NodeId("feature-a"), kind="feature", payload="not-a-feature")


def test_graph_node_validates_id_kind_payload_and_payload_keys() -> None:
    with pytest.raises(ValueError, match="id"):
        GraphNode(id=NodeId(""), kind="part", payload="part")
    with pytest.raises(ValueError, match="kind"):
        GraphNode(id=NodeId("part-1"), kind=cast(GraphNodeKind, "unknown"), payload="part")
    with pytest.raises(TypeError, match="only valid"):
        GraphNode(id=NodeId("part-1"), kind="part", payload=_feature("gene"))
    with pytest.raises(ValueError, match="payload keys"):
        GraphNode(id=NodeId("part-1"), kind="part", payload=(("", "bad"),))


def test_edge_validates_endpoint_ids_and_annotation_keys() -> None:
    with pytest.raises(ValueError, match="source"):
        Edge(source=NodeId(""), target=NodeId("part-1"), kind=EdgeKind.ADJACENCY)
    with pytest.raises(ValueError, match="target"):
        Edge(source=NodeId("part-1"), target=NodeId(""), kind=EdgeKind.ADJACENCY)
    with pytest.raises(ValueError, match="annotation"):
        Edge(
            source=NodeId("part-1"),
            target=NodeId("part-2"),
            kind=EdgeKind.ADJACENCY,
            annotations=(("", "bad"),),
        )


def test_canonical_json_rejects_non_object_payload() -> None:
    with pytest.raises(TypeError, match="object"):
        ConstructGraph.from_canonical_json("[]")


def test_canonical_dict_rejects_malformed_top_level_shapes() -> None:
    graph_data = _round_trip_graph().to_canonical_dict()

    malformed_nodes = deepcopy(graph_data)
    malformed_nodes["nodes"] = "not-a-list"
    with pytest.raises(TypeError, match="nodes"):
        ConstructGraph.from_canonical_dict(malformed_nodes)

    malformed_node = deepcopy(graph_data)
    cast(list[object], malformed_node["nodes"])[0] = 1
    with pytest.raises(TypeError, match="node"):
        ConstructGraph.from_canonical_dict(malformed_node)

    malformed_topology = deepcopy(graph_data)
    malformed_topology["topology"] = "plasmid"
    with pytest.raises(ValueError, match="topology"):
        ConstructGraph.from_canonical_dict(malformed_topology)


def test_canonical_dict_rejects_malformed_node_payloads() -> None:
    graph_data = _round_trip_graph().to_canonical_dict()

    bad_node_kind = deepcopy(graph_data)
    first_node = cast(dict[str, object], cast(list[object], bad_node_kind["nodes"])[0])
    first_node["kind"] = "unknown"
    with pytest.raises(ValueError, match="graph node kind"):
        ConstructGraph.from_canonical_dict(bad_node_kind)

    bad_payload_kind = deepcopy(graph_data)
    payload = cast(
        dict[str, object],
        cast(dict[str, object], cast(list[object], bad_payload_kind["nodes"])[0])["payload"],
    )
    payload["kind"] = "unknown"
    with pytest.raises(ValueError, match="payload kind"):
        ConstructGraph.from_canonical_dict(bad_payload_kind)

    bad_text_payload = deepcopy(graph_data)
    text_node = cast(dict[str, object], cast(list[object], bad_text_payload["nodes"])[0])
    text_node["payload"] = {"kind": "text", "value": 42}
    with pytest.raises(TypeError, match="string"):
        ConstructGraph.from_canonical_dict(bad_text_payload)


def test_canonical_dict_rejects_malformed_nested_values() -> None:
    graph_data = _round_trip_graph().to_canonical_dict()

    bad_annotation = deepcopy(graph_data)
    first_edge = cast(dict[str, object], cast(list[object], bad_annotation["edges"])[0])
    first_edge["annotations"] = {"bad": 1}
    with pytest.raises(TypeError, match="annotation"):
        ConstructGraph.from_canonical_dict(bad_annotation)

    bad_location = deepcopy(graph_data)
    feature_payload = _feature_payload_dict(bad_location)
    first_location = cast(dict[str, object], cast(list[object], feature_payload["locations"])[0])
    first_location["strand"] = "?"
    with pytest.raises(ValueError, match="strand"):
        ConstructGraph.from_canonical_dict(bad_location)

    bad_phase = deepcopy(graph_data)
    first_location = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_phase)["locations"])[0],
    )
    first_location["phase"] = 4
    with pytest.raises(ValueError, match="phase"):
        ConstructGraph.from_canonical_dict(bad_phase)

    bad_qualifier_type = deepcopy(graph_data)
    first_qualifier = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_qualifier_type)["qualifiers"])[0],
    )
    first_qualifier["value_type"] = "binary"
    with pytest.raises(ValueError, match="value_type"):
        ConstructGraph.from_canonical_dict(bad_qualifier_type)


def test_canonical_dict_rejects_malformed_scalar_types() -> None:
    graph_data = _round_trip_graph().to_canonical_dict()

    bad_int = deepcopy(graph_data)
    first_location = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_int)["locations"])[0],
    )
    first_location["start"] = "zero"
    with pytest.raises(TypeError, match="integer"):
        ConstructGraph.from_canonical_dict(bad_int)

    bad_bool = deepcopy(graph_data)
    first_location = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_bool)["locations"])[0],
    )
    first_location["between_base"] = "false"
    with pytest.raises(TypeError, match="boolean"):
        ConstructGraph.from_canonical_dict(bad_bool)

    bad_optional_str = deepcopy(graph_data)
    first_qualifier = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_optional_str)["qualifiers"])[0],
    )
    first_qualifier["provenance"] = 123
    with pytest.raises(TypeError, match="string or null"):
        ConstructGraph.from_canonical_dict(bad_optional_str)


def test_canonical_dict_rejects_malformed_structured_qualifier_pairs() -> None:
    graph = ConstructGraph(
        nodes=(
            GraphNode(
                id=NodeId("feature-a"),
                kind="feature",
                payload=FeatureV14(
                    role="SO:0000316",
                    qualifiers=(
                        Qualifier(
                            namespace="SnapGene",
                            key="style",
                            value=(("color", "blue"),),
                            value_type="structured",
                            order=0,
                        ),
                    ),
                    locations=(LocationV14(start=0, end=1, strand="+", phase="."),),
                    parent_sequence_id="seq-1",
                ),
            ),
        ),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )
    graph_data = graph.to_canonical_dict()

    bad_pair_container = deepcopy(graph_data)
    first_qualifier = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_pair_container)["qualifiers"])[0],
    )
    first_qualifier["value"] = "not-a-list"
    with pytest.raises(TypeError, match="structured qualifier value"):
        ConstructGraph.from_canonical_dict(bad_pair_container)

    bad_pair = deepcopy(graph_data)
    first_qualifier = cast(
        dict[str, object],
        cast(list[object], _feature_payload_dict(bad_pair)["qualifiers"])[0],
    )
    first_qualifier["value"] = [["too", "many", "items"]]
    with pytest.raises(TypeError, match="key/value pairs"):
        ConstructGraph.from_canonical_dict(bad_pair)


def _feature_payload_dict(graph_data: dict[str, object]) -> dict[str, object]:
    nodes = cast(list[object], graph_data["nodes"])
    for node in nodes:
        node_data = cast(dict[str, object], node)
        payload = cast(dict[str, object], node_data["payload"])
        if payload["kind"] == "feature":
            return cast(dict[str, object], payload["value"])
    raise AssertionError("fixture graph did not contain a feature node")


@settings(max_examples=1000)
@given(
    st.lists(
        st.text(alphabet="abc", min_size=1, max_size=8),
        min_size=1,
        max_size=12,
        unique=True,
    ),
)
def test_node_order_does_not_change_canonical_json(node_ids: list[str]) -> None:
    nodes = tuple(_part_node(node_id) for node_id in node_ids)
    reversed_nodes = tuple(reversed(nodes))

    first = ConstructGraph(nodes=nodes, edges=(), topology="linear", sequence_record=_record())
    second = ConstructGraph(
        nodes=reversed_nodes,
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )

    assert first.canonical_json() == second.canonical_json()
