"""
module_id: engine.compatibility.host_constraints
file: src/engine/compatibility/host_constraints.py
task_id: T-504

Construct-level facts consumed by host compatibility checks.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.construct import Construct
from domain.types.ids import MarkerId, OriginId, PartId
from domain.types.module import Module, OneOf, PartOrVariant
from domain.types.part import Part

ORIGIN_ROLE_TOKENS = frozenset({"origin", "replication_origin", "so:0000296"})
MARKER_ROLE_TOKENS = frozenset({"marker", "selection_marker", "selectable_marker"})


@dataclass(frozen=True)
class DesignCompatibilityProfile:
    origins: frozenset[OriginId]
    markers: frozenset[MarkerId]
    parts: tuple[Part, ...]

    @property
    def part_ids(self) -> frozenset[PartId]:
        return frozenset(part.id for part in self.parts)


def extract_design_compatibility_profile(construct: Construct) -> DesignCompatibilityProfile:
    parts = tuple(part for module in construct.modules for part in _iter_parts(module))
    return DesignCompatibilityProfile(
        origins=frozenset(_origin_id(part) for part in parts if _is_origin(part)),
        markers=frozenset(_marker_id(part) for part in parts if _is_marker(part)),
        parts=parts,
    )


def _iter_parts(module: Module) -> tuple[Part, ...]:
    parts: list[Part] = []
    for item in module.parts:
        parts.extend(_parts_from_variant(item))
    return tuple(parts)


def _parts_from_variant(item: PartOrVariant) -> tuple[Part, ...]:
    if isinstance(item, Part):
        return (item,)
    if isinstance(item, OneOf):
        return tuple(item.candidates)
    return ()


def _is_origin(part: Part) -> bool:
    role = str(part.role).lower()
    return any(token in role for token in ORIGIN_ROLE_TOKENS) or str(part.id).startswith("origin.")


def _is_marker(part: Part) -> bool:
    role = str(part.role).lower()
    return any(token in role for token in MARKER_ROLE_TOKENS) or str(part.id).startswith("marker.")


def _origin_id(part: Part) -> OriginId:
    return OriginId(str(part.id))


def _marker_id(part: Part) -> MarkerId:
    return MarkerId(str(part.id))


__all__ = [
    "DesignCompatibilityProfile",
    "extract_design_compatibility_profile",
]
