"""
module_id: engine.controls.generator
file: src/engine/controls/generator.py
task_id: T-804

Deterministic control-set generator.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.controls import ControlDesign, ControlKind, ControlSet


@dataclass(frozen=True)
class ControlGenerationInput:
    construct_id: str
    host_role: str
    assembly_method: str
    cargo_classes: tuple[str, ...] = ()
    vector_system_classes: tuple[str, ...] = ()
    intended_readout: str = "design verification"
    library_size: int = 1
    biological_replicates: int = 3
    require_vehicle_control: bool | None = None
    include_process_control: bool = True

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.host_role:
            raise ValueError("host_role cannot be empty")
        if not self.assembly_method:
            raise ValueError("assembly_method cannot be empty")
        if not self.intended_readout:
            raise ValueError("intended_readout cannot be empty")
        if self.library_size < 1:
            raise ValueError("library_size must be at least 1")
        if self.biological_replicates < 1:
            raise ValueError("biological_replicates must be at least 1")
        _require_non_empty_items(self.cargo_classes, "cargo_classes")
        _require_non_empty_items(self.vector_system_classes, "vector_system_classes")

    @property
    def vehicle_control_required(self) -> bool:
        if self.require_vehicle_control is not None:
            return self.require_vehicle_control
        tags = _normalised_tags(
            (self.host_role, self.assembly_method, *self.cargo_classes, *self.vector_system_classes)
        )
        return bool(tags & {"mammalian", "plant", "agrobacterium", "aav", "lentivirus", "vlp"})


class ControlSetGenerator:
    """Generate a deterministic first-class control set for a draft design."""

    def generate(self, request: ControlGenerationInput) -> ControlSet:
        controls = [
            _positive_control(request),
            _negative_control(request),
        ]
        if request.include_process_control:
            controls.append(_process_control(request))
        if request.vehicle_control_required:
            controls.append(_vehicle_control(request))
        if request.library_size > 1:
            controls.append(_library_specific_control(request))
        return ControlSet(construct_id=request.construct_id, controls=tuple(controls))


def generate_controls(request: ControlGenerationInput) -> ControlSet:
    return ControlSetGenerator().generate(request)


def _positive_control(request: ControlGenerationInput) -> ControlDesign:
    readout = _readout_label(request)
    return ControlDesign(
        control_id=_control_id(request, "positive"),
        kind=ControlKind.POSITIVE,
        purpose=(
            f"Host-matched positive control for {request.host_role} using "
            f"{readout} to confirm assay sensitivity"
        ),
        expected_observation=(
            f"Detect {readout} above the negative and vehicle-control baseline"
        ),
    )


def _negative_control(request: ControlGenerationInput) -> ControlDesign:
    readout = _readout_label(request)
    return ControlDesign(
        control_id=_control_id(request, "negative"),
        kind=ControlKind.NEGATIVE,
        purpose=(
            f"Matched no-cargo or non-expressing construct for {request.host_role} "
            f"to establish absence-of-signal baseline"
        ),
        expected_observation=f"No cargo-specific {readout}; baseline-only signal",
    )


def _process_control(request: ControlGenerationInput) -> ControlDesign:
    return ControlDesign(
        control_id=_control_id(request, "process"),
        kind=ControlKind.PROCESS,
        purpose=(
            f"Assembly-process control for {request.assembly_method} to distinguish "
            "workflow failure from construct-specific behaviour"
        ),
        expected_observation=(
            "Control product passes the same sequence/map verification checkpoints as the design"
        ),
    )


def _vehicle_control(request: ControlGenerationInput) -> ControlDesign:
    return ControlDesign(
        control_id=_control_id(request, "vehicle"),
        kind=ControlKind.VEHICLE,
        purpose=(
            f"Vehicle/mock control for {request.host_role} delivery context without cargo payload"
        ),
        expected_observation=(
            f"Vehicle background remains at or below the negative-control "
            f"{_readout_label(request)} baseline"
        ),
    )


def _library_specific_control(request: ControlGenerationInput) -> ControlDesign:
    return ControlDesign(
        control_id=_control_id(request, "library"),
        kind=ControlKind.LIBRARY_SPECIFIC,
        purpose=(
            f"Representative library controls for {request.library_size} variants with "
            f"n={request.biological_replicates} biological replicate recommendation"
        ),
        expected_observation=(
            "Low, middle, and high representative variants remain distinguishable from "
            "positive and negative controls"
        ),
    )


def _readout_label(request: ControlGenerationInput) -> str:
    tags = _normalised_tags((*request.cargo_classes, request.intended_readout))
    if tags & {"gfp", "mcherry", "fluorescent", "fluorescence", "reporter"}:
        return "reporter fluorescence"
    if tags & {"enzyme", "enzymatic", "catalytic"}:
        return "enzymatic activity"
    if tags & {"vlp", "aav", "lentivirus", "phage"}:
        return "particle or delivery readout"
    if tags & {"protein", "expression"}:
        return "protein-expression signal"
    return request.intended_readout


def _control_id(request: ControlGenerationInput, suffix: str) -> str:
    return f"{_slug(request.construct_id)}.{suffix}.{_slug(request.host_role)}"


def _normalised_tags(values: tuple[str, ...]) -> frozenset[str]:
    return frozenset(_slug(value) for value in values if value.strip())


def _slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def _require_non_empty_items(values: tuple[str, ...], field_name: str) -> None:
    if any(not value for value in values):
        raise ValueError(f"{field_name} cannot contain empty values")
