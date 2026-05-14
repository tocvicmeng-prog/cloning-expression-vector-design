"""
module_id: tests.app.test_design_plan_orchestrator_t805a
file: tests/app/test_design_plan_orchestrator_t805a.py
task_id: T-805a
"""

from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from pathlib import Path

from adapter.catalogue import load_catalogue, schema_for_catalogue
from app.design_plan_orchestrator import (
    DesignPlanOrchestrator,
    DraftDesignBundle,
    DraftDesignBundleRequest,
)
from domain.events import (
    ControlSetRendered,
    DesignRealisationPlanRendered,
    DomainEvent,
    EventStream,
    RiskAdvisoryReportRendered,
)
from domain.sequence import DnaSequence, MoleculeType, SequenceRecord, sha256_text
from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.ids import AssemblyMethodId
from engine.controls import ControlGenerationInput
from engine.design_plan import DesignPlanInput, render_json, render_markdown, render_pdf
from engine.risk_classification import (
    RiskAdvisoryCatalogue,
    RiskClassificationEngine,
    RiskClassificationInput,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 5, 14, 12, 30, tzinfo=UTC)


def test_orchestrator_renders_draft_bundle_and_appends_design_events() -> None:
    event_log = MemoryDesignEventLog()
    request = _request()
    bundle = DesignPlanOrchestrator(_risk_engine(), event_log=event_log).render_draft_bundle(
        request
    )

    assert bundle.design_session_id == "session-805a"
    assert bundle.construct_id == "construct-805a"
    assert bundle.design_plan_json == render_json(bundle.design_plan)
    assert bundle.design_plan_markdown == render_markdown(bundle.design_plan)
    assert bundle.design_plan_pdf == render_pdf(bundle.design_plan)
    assert bundle.control_validation.valid
    assert bundle.risk_advisory_report.advisories
    assert str(bundle.content_hash)
    assert tuple(event.event_type for event in bundle.events) == (
        "DesignRealisationPlanRendered",
        "ControlSetRendered",
        "RiskAdvisoryReportRendered",
    )
    assert all(event.stream is EventStream.DESIGN for event in bundle.events)
    assert event_log.events["session-805a"] == list(bundle.events)
    assert isinstance(bundle.events[0], DesignRealisationPlanRendered)
    assert isinstance(bundle.events[1], ControlSetRendered)
    assert isinstance(bundle.events[2], RiskAdvisoryReportRendered)


def test_draft_bundle_canonical_json_is_deterministic() -> None:
    orchestrator = DesignPlanOrchestrator(_risk_engine())
    first = orchestrator.render_draft_bundle(_request())
    second = orchestrator.render_draft_bundle(_request())

    assert first.content_hash == second.content_hash
    assert first.canonical_json() == second.canonical_json()


def test_draft_bundle_shape_excludes_operational_fields() -> None:
    forbidden = {"sop", "screening", "vendor", "operational", "authorisation"}
    names = _dataclass_field_names(DraftDesignBundle)
    bundle = DesignPlanOrchestrator(_risk_engine()).render_draft_bundle(_request())

    assert all(not any(term in name.lower() for term in forbidden) for name in names)
    assert all(
        event_cls.__name__
        not in {"ScreeningCompleted", "OperationalProtocolAuthorised", "SopRendered"}
        for event_cls in {type(event) for event in bundle.events}
    )


def test_design_plan_orchestrator_does_not_import_gated_or_export_events() -> None:
    path = ROOT / "src" / "app" / "design_plan_orchestrator.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_imports = {
        "domain.types.sop_protected",
        "ScreeningCompleted",
        "OperationalProtocolAuthorised",
        "SopRendered",
    }
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("domain.types.sop_protected"):
                offenders.append(module)
            offenders.extend(alias.name for alias in node.names if alias.name in forbidden_imports)
        if isinstance(node, ast.Import):
            offenders.extend(alias.name for alias in node.names if alias.name in forbidden_imports)

    assert offenders == []


class MemoryDesignEventLog:
    def __init__(self) -> None:
        self.events: dict[str, list[DomainEvent]] = {}

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


def _request() -> DraftDesignBundleRequest:
    assembly_plan = _assembly_plan()
    return DraftDesignBundleRequest(
        design_session_id="session-805a",
        actor_id="design-plan-orchestrator",
        occurred_at_utc=NOW,
        event_id_prefix="session-805a.draft",
        design_plan_input=DesignPlanInput(
            design_session_id="session-805a",
            construct_id="construct-805a",
            construct_version="1",
            assembly_plan=assembly_plan,
            primer_set=("vector_fwd", "vector_rev", "insert_fwd", "insert_rev"),
            biosafety_classification="BSL-2",
            validation_report_hashes=(str(sha256_text("validation-805a")),),
        ),
        control_input=ControlGenerationInput(
            construct_id="construct-805a",
            host_role="mammalian expression",
            assembly_method="Golden Gate",
            cargo_classes=("MS2", "mCherry reporter"),
            vector_system_classes=("AAV",),
            intended_readout="fluorescence",
            library_size=4,
        ),
        risk_classification_input=RiskClassificationInput(
            design_session_id="session-805a",
            construct_id="construct-805a",
            construct_checksum=assembly_plan.expected_product.checksum,
            construct_version="1",
            biosafety_tier="BSL-2",
            cargo_classes=("MS2",),
            vector_system_classes=("AAV",),
        ),
    )


def _assembly_plan() -> AssemblyPlanSummary:
    return AssemblyPlanSummary(
        method=AssemblyMethodId("golden-gate"),
        fragments=("vector", "insert"),
        expected_product=SequenceRecord(
            id="construct-805a-product",
            sequence=DnaSequence("ATGCGTACGTAG"),
            topology="linear",
            molecule_type=MoleculeType.DS_DNA,
        ),
        verification_checkpoints=("Review vector-insert junction",),
    )


def _risk_engine() -> RiskClassificationEngine:
    path = ROOT / "catalogues" / "risk_advisories.yaml"
    payload = load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload
    return RiskClassificationEngine(RiskAdvisoryCatalogue.from_payload(payload))


def _dataclass_field_names(value: type[object]) -> tuple[str, ...]:
    assert is_dataclass(value)
    return tuple(field.name for field in fields(value))
