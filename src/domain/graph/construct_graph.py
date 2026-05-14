"""
module_id: domain.graph.construct_graph
file: src/domain/graph/construct_graph.py
task_id: T-302

Canonical construct graph with deterministic JSON and feature-table derivation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, cast

from domain.graph.edges import AnnotationItems, Edge, EdgeKind
from domain.graph.nodes import GraphNode, NodeId, NodePayload
from domain.sequence import (
    CompoundLocationKind,
    FeatureV14,
    LocationFuzziness,
    LocationV14,
    Qualifier,
    SequenceRecord,
    Topology,
)

JsonScalar = str | int | float | bool | None
JsonObject = dict[str, object]
PayloadKind = Literal["feature", "text", "mapping"]


@dataclass(frozen=True)
class ConstructGraph:
    nodes: tuple[GraphNode, ...]
    edges: tuple[Edge, ...]
    topology: Topology
    sequence_record: SequenceRecord

    def __post_init__(self) -> None:
        if not self.nodes:
            raise ValueError("construct graph must contain at least one node")
        if self.topology not in {"linear", "circular"}:
            raise ValueError("construct graph topology must be linear or circular")
        if self.sequence_record.topology != self.topology:
            raise ValueError("construct graph topology must match sequence_record topology")

        sorted_nodes = tuple(sorted(self.nodes, key=lambda node: str(node.id)))
        node_ids: set[NodeId] = set()
        for node in sorted_nodes:
            if node.id in node_ids:
                raise ValueError(f"duplicate graph node id: {node.id}")
            node_ids.add(node.id)

        sorted_edges = tuple(
            sorted(
                self.edges,
                key=lambda edge: (
                    str(edge.source),
                    str(edge.target),
                    edge.kind.value,
                    edge.annotations,
                ),
            ),
        )
        for edge in sorted_edges:
            if edge.source not in node_ids:
                raise ValueError(f"edge source does not exist: {edge.source}")
            if edge.target not in node_ids:
                raise ValueError(f"edge target does not exist: {edge.target}")

        object.__setattr__(self, "nodes", sorted_nodes)
        object.__setattr__(self, "edges", sorted_edges)

    @property
    def node_map(self) -> dict[NodeId, GraphNode]:
        return {node.id: node for node in self.nodes}

    @property
    def feature_table(self) -> tuple[FeatureV14, ...]:
        return derive_feature_table(self)

    def with_node(self, node: GraphNode) -> ConstructGraph:
        return ConstructGraph(
            nodes=(*self.nodes, node),
            edges=self.edges,
            topology=self.topology,
            sequence_record=self.sequence_record,
        )

    def with_edge(self, edge: Edge) -> ConstructGraph:
        return ConstructGraph(
            nodes=self.nodes,
            edges=(*self.edges, edge),
            topology=self.topology,
            sequence_record=self.sequence_record,
        )

    def to_canonical_dict(self) -> JsonObject:
        return {
            "edges": [_edge_to_dict(edge) for edge in self.edges],
            "nodes": [_node_to_dict(node) for node in self.nodes],
            "sequence_record": self.sequence_record.to_dict(),
            "topology": self.topology,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_canonical_dict(cls, data: JsonObject) -> ConstructGraph:
        nodes = tuple(_node_from_dict(item) for item in _expect_list(data, "nodes"))
        edges = tuple(_edge_from_dict(item) for item in _expect_list(data, "edges"))
        sequence_record = SequenceRecord.from_dict(
            cast(dict[str, str | int], _expect_dict(data, "sequence_record")),
        )
        topology = _topology_from_value(data.get("topology"))
        return cls(
            nodes=nodes,
            edges=edges,
            topology=topology,
            sequence_record=sequence_record,
        )

    @classmethod
    def from_canonical_json(cls, payload: str) -> ConstructGraph:
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise TypeError("construct graph JSON must decode to an object")
        return cls.from_canonical_dict(cast(JsonObject, loaded))


def derive_feature_table(graph: ConstructGraph) -> tuple[FeatureV14, ...]:
    return tuple(cast(FeatureV14, node.payload) for node in graph.nodes if node.kind == "feature")


def _node_to_dict(node: GraphNode) -> JsonObject:
    payload_kind, payload_value = _payload_to_dict(node.payload)
    return {
        "id": str(node.id),
        "kind": node.kind,
        "payload": {"kind": payload_kind, "value": payload_value},
    }


def _node_from_dict(raw: object) -> GraphNode:
    data = _object_from_raw(raw, "node")
    payload_data = _expect_dict(data, "payload")
    payload = _payload_from_dict(
        _payload_kind_from_value(payload_data.get("kind")),
        payload_data.get("value"),
    )
    kind = _node_kind_from_value(data.get("kind"))
    return GraphNode(
        id=NodeId(_expect_str(data, "id")),
        kind=kind,
        payload=payload,
    )


def _edge_to_dict(edge: Edge) -> JsonObject:
    return {
        "annotations": dict(edge.annotations),
        "kind": edge.kind.value,
        "source": str(edge.source),
        "target": str(edge.target),
    }


def _edge_from_dict(raw: object) -> Edge:
    data = _object_from_raw(raw, "edge")
    return Edge(
        source=NodeId(_expect_str(data, "source")),
        target=NodeId(_expect_str(data, "target")),
        kind=EdgeKind(_expect_str(data, "kind")),
        annotations=_annotation_items_from_object(data.get("annotations", {})),
    )


def _payload_to_dict(payload: NodePayload) -> tuple[PayloadKind, object]:
    if isinstance(payload, FeatureV14):
        return "feature", _feature_to_dict(payload)
    if isinstance(payload, str):
        return "text", payload
    return "mapping", dict(payload)


def _payload_from_dict(kind: PayloadKind, value: object) -> NodePayload:
    if kind == "feature":
        return _feature_from_dict(_object_from_raw(value, "feature payload"))
    if kind == "text":
        if not isinstance(value, str):
            raise TypeError("text graph node payload must be a string")
        return value
    return _annotation_items_from_object(value)


def _feature_to_dict(feature: FeatureV14) -> JsonObject:
    return {
        "evidence": list(feature.evidence),
        "locations": [_location_to_dict(location) for location in feature.locations],
        "parent_sequence_id": feature.parent_sequence_id,
        "qualifiers": [_qualifier_to_dict(qualifier) for qualifier in feature.ordered_qualifiers],
        "role": feature.role,
        "sub_features": [_feature_to_dict(sub_feature) for sub_feature in feature.sub_features],
    }


def _feature_from_dict(data: JsonObject) -> FeatureV14:
    return FeatureV14(
        role=_expect_str(data, "role"),
        qualifiers=tuple(_qualifier_from_dict(item) for item in _expect_list(data, "qualifiers")),
        locations=tuple(_location_from_dict(item) for item in _expect_list(data, "locations")),
        parent_sequence_id=_expect_str(data, "parent_sequence_id"),
        evidence=tuple(
            _expect_str_item(item, "feature evidence") for item in _expect_list(data, "evidence")
        ),
        sub_features=tuple(
            _feature_from_dict(_object_from_raw(item, "sub feature"))
            for item in _expect_list(data, "sub_features")
        ),
    )


def _qualifier_to_dict(qualifier: Qualifier) -> JsonObject:
    value = qualifier.value
    if isinstance(value, tuple):
        value = tuple((key, item) for key, item in value)
    return {
        "key": qualifier.key,
        "namespace": qualifier.namespace,
        "order": qualifier.order,
        "provenance": qualifier.provenance,
        "value": value,
        "value_type": qualifier.value_type,
    }


def _qualifier_from_dict(raw: object) -> Qualifier:
    data = _object_from_raw(raw, "qualifier")
    value: object = data.get("value")
    value_type = _qualifier_value_type_from_value(data.get("value_type"))
    if value_type == "structured":
        value = tuple(
            (_expect_str_item(pair[0], "structured qualifier key"), pair[1])
            for pair in _expect_pair_list(value, "structured qualifier value")
        )
    return Qualifier(
        namespace=_expect_str(data, "namespace"),
        key=_expect_str(data, "key"),
        value=cast(str | bool | int | float | tuple[tuple[str, object], ...], value),
        value_type=value_type,
        order=_expect_int(data, "order"),
        provenance=_optional_str(data.get("provenance"), "provenance"),
    )


def _location_to_dict(location: LocationV14) -> JsonObject:
    return {
        "between_base": location.between_base,
        "circular_wrap": location.circular_wrap,
        "complement_compound": location.complement_compound,
        "end": location.end,
        "end_fuzziness": location.end_fuzziness.value,
        "partial_at_3p": location.partial_at_3p,
        "partial_at_5p": location.partial_at_5p,
        "phase": location.phase,
        "remote_accession": location.remote_accession,
        "start": location.start,
        "start_fuzziness": location.start_fuzziness.value,
        "strand": location.strand,
        "sub_kind": None if location.sub_kind is None else location.sub_kind.value,
        "sub_locations": [_location_to_dict(child) for child in location.sub_locations],
    }


def _location_from_dict(raw: object) -> LocationV14:
    data = _object_from_raw(raw, "location")
    sub_kind_value = data.get("sub_kind")
    return LocationV14(
        start=_expect_int(data, "start"),
        end=_expect_int(data, "end"),
        strand=_strand_from_value(data.get("strand")),
        phase=_phase_from_value(data.get("phase")),
        start_fuzziness=LocationFuzziness(_expect_str(data, "start_fuzziness")),
        end_fuzziness=LocationFuzziness(_expect_str(data, "end_fuzziness")),
        circular_wrap=_expect_bool(data, "circular_wrap"),
        between_base=_expect_bool(data, "between_base"),
        sub_locations=tuple(
            _location_from_dict(item) for item in _expect_list(data, "sub_locations")
        ),
        sub_kind=(
            None if sub_kind_value is None else CompoundLocationKind(_expect_str(data, "sub_kind"))
        ),
        complement_compound=_expect_bool(data, "complement_compound"),
        remote_accession=_optional_str(data.get("remote_accession"), "remote_accession"),
        partial_at_5p=_expect_bool(data, "partial_at_5p"),
        partial_at_3p=_expect_bool(data, "partial_at_3p"),
    )


def _expect_dict(data: JsonObject, key: str) -> JsonObject:
    return _object_from_raw(data.get(key), key)


def _object_from_raw(raw: object, name: str) -> JsonObject:
    if not isinstance(raw, dict):
        raise TypeError(f"{name} must be an object")
    return cast(JsonObject, raw)


def _expect_list(data: JsonObject, key: str) -> list[object]:
    value = data.get(key)
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list")
    return value


def _expect_pair_list(raw: object, name: str) -> list[tuple[object, object]]:
    if not isinstance(raw, list):
        raise TypeError(f"{name} must be a list")
    pairs: list[tuple[object, object]] = []
    for item in raw:
        if not isinstance(item, list | tuple) or len(item) != 2:
            raise TypeError(f"{name} items must be key/value pairs")
        pairs.append((item[0], item[1]))
    return pairs


def _expect_str(data: JsonObject, key: str) -> str:
    return _expect_str_item(data.get(key), key)


def _expect_str_item(raw: object, name: str) -> str:
    if not isinstance(raw, str):
        raise TypeError(f"{name} must be a string")
    return raw


def _optional_str(raw: object, name: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise TypeError(f"{name} must be a string or null")
    return raw


def _expect_int(data: JsonObject, key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{key} must be an integer")
    return value


def _expect_bool(data: JsonObject, key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _topology_from_value(raw: object) -> Topology:
    if raw == "linear" or raw == "circular":
        return raw
    raise ValueError("topology must be linear or circular")


def _node_kind_from_value(raw: object) -> Literal["part", "feature", "module"]:
    if raw == "part" or raw == "feature" or raw == "module":
        return raw
    raise ValueError("graph node kind must be part, feature, or module")


def _payload_kind_from_value(raw: object) -> PayloadKind:
    if raw == "feature" or raw == "text" or raw == "mapping":
        return raw
    raise ValueError("payload kind must be feature, text, or mapping")


def _strand_from_value(raw: object) -> Literal["+", "-", "."]:
    if raw == "+" or raw == "-" or raw == ".":
        return raw
    raise ValueError("location strand must be '+', '-', or '.'")


def _phase_from_value(raw: object) -> Literal[0, 1, 2, "."]:
    if raw == 0 or raw == 1 or raw == 2 or raw == ".":
        return raw
    raise ValueError("location phase must be 0, 1, 2, or '.'")


def _qualifier_value_type_from_value(
    raw: object,
) -> Literal[
    "string",
    "boolean",
    "integer",
    "float",
    "url",
    "ontology_term",
    "structured",
]:
    if raw in {"string", "boolean", "integer", "float", "url", "ontology_term", "structured"}:
        return cast(
            Literal[
                "string",
                "boolean",
                "integer",
                "float",
                "url",
                "ontology_term",
                "structured",
            ],
            raw,
        )
    raise ValueError("unsupported qualifier value_type")


def _annotation_items_from_object(raw: object) -> AnnotationItems:
    data = _object_from_raw(raw, "annotations")
    items: list[tuple[str, str]] = []
    for key, value in data.items():
        if not isinstance(value, str):
            raise TypeError("annotation values must be strings")
        items.append((key, value))
    return tuple(sorted(items))
