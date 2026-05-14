"""
module_id: tests.engine.test_controls_t804
file: tests/engine/test_controls_t804.py
task_id: T-804
"""

from __future__ import annotations

import ast
from pathlib import Path

from domain.types.controls import ControlDesign, ControlKind, ControlSet
from engine.controls import (
    ControlGenerationInput,
    ControlSetGenerator,
    ControlValidationSeverity,
    generate_controls,
    validate_control_set,
)

ROOT = Path(__file__).resolve().parents[2]


def test_controls_generator_emits_host_and_library_matched_controls() -> None:
    request = ControlGenerationInput(
        construct_id="construct-804",
        host_role="mammalian expression",
        assembly_method="Golden Gate",
        cargo_classes=("mCherry reporter",),
        vector_system_classes=("AAV",),
        intended_readout="fluorescence",
        library_size=12,
        biological_replicates=3,
    )

    control_set = ControlSetGenerator().generate(request)
    by_kind = {control.kind: control for control in control_set.controls}

    assert set(by_kind) == {
        ControlKind.POSITIVE,
        ControlKind.NEGATIVE,
        ControlKind.PROCESS,
        ControlKind.VEHICLE,
        ControlKind.LIBRARY_SPECIFIC,
    }
    assert "mammalian expression" in by_kind[ControlKind.POSITIVE].purpose
    assert "reporter fluorescence" in by_kind[ControlKind.POSITIVE].expected_observation
    assert "No cargo-specific" in by_kind[ControlKind.NEGATIVE].expected_observation
    assert "n=3" in by_kind[ControlKind.LIBRARY_SPECIFIC].purpose
    assert validate_control_set(request, control_set).valid


def test_controls_generator_keeps_simple_bacterial_design_minimal_and_deterministic() -> None:
    request = ControlGenerationInput(
        construct_id="construct-804",
        host_role="bacterial cloning",
        assembly_method="Gibson",
        cargo_classes=("protein",),
        intended_readout="colony PCR",
    )

    first = generate_controls(request)
    second = generate_controls(request)

    assert first == second
    assert tuple(control.kind for control in first.controls) == (
        ControlKind.POSITIVE,
        ControlKind.NEGATIVE,
        ControlKind.PROCESS,
    )
    assert validate_control_set(request, first).findings == ()


def test_control_validation_flags_missing_context_required_controls() -> None:
    request = ControlGenerationInput(
        construct_id="construct-804",
        host_role="plant expression",
        assembly_method="Golden Gate",
        vector_system_classes=("Agrobacterium",),
        library_size=6,
        biological_replicates=1,
    )
    incomplete = ControlSet(
        construct_id="construct-804",
        controls=(
            ControlDesign(
                control_id="positive",
                kind=ControlKind.POSITIVE,
                purpose="Host-matched positive control for plant expression",
                expected_observation="Detect signal above baseline",
            ),
            ControlDesign(
                control_id="negative",
                kind=ControlKind.NEGATIVE,
                purpose="No-cargo baseline",
                expected_observation="No signal",
            ),
        ),
    )

    report = validate_control_set(request, incomplete)
    errors = {finding.rule_id for finding in report.errors}
    warnings = {finding.rule_id for finding in report.warnings}

    assert not report.valid
    assert {
        "control.vehicle_missing",
        "control.library_specific_missing",
    } <= errors
    assert {
        "control.process_missing",
        "control.replicates_low",
    } <= warnings
    assert all(finding.severity in ControlValidationSeverity for finding in report.findings)


def test_controls_engine_package_does_not_import_gated_namespace() -> None:
    controls_dir = ROOT / "src" / "engine" / "controls"
    offenders: list[str] = []
    for path in controls_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (
                node.module is not None and node.module.startswith("domain.types.sop_protected")
            ):
                offenders.append(str(path.relative_to(ROOT)))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("domain.types.sop_protected"):
                        offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
