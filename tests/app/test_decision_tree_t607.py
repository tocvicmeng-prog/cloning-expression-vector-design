"""
module_id: tests.app.test_decision_tree_t607
file: tests/app/test_decision_tree_t607.py
task_id: T-607
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import pytest

from app.decision_flow import DECISION_STEP_ORDER, DecisionContext, DecisionStep
from app.decision_tree import DecisionTree
from app.design_service import DesignService
from domain.events import DomainEvent
from domain.security import InstitutionId, PrincipalId, SecurityRole, UserPrincipal
from engine.session import DesignSession, InMemorySnapshotStore, SessionState

NOW = datetime(2026, 5, 14, tzinfo=UTC)


@dataclass(frozen=True)
class InMemoryCatalogue:
    items: tuple[Mapping[str, object], ...]

    def list_items(self) -> tuple[Mapping[str, object], ...]:
        return self.items


@dataclass
class InMemoryDesignEventLog:
    events: dict[str, list[DomainEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id

    def read_events(self, stream_id: str) -> tuple[DomainEvent, ...]:
        return tuple(self.events.get(stream_id, ()))


@dataclass
class InMemoryProjectStore:
    sessions: dict[str, DesignSession] = field(default_factory=dict)

    def save_session(self, session: DesignSession) -> str:
        self.sessions[session.session_id] = session
        return session.session_id


@pytest.mark.parametrize(
    "step",
    [
        DecisionStep.OBJECTIVE,
        DecisionStep.HOST,
        DecisionStep.CARGO,
        DecisionStep.EXPRESSION,
        DecisionStep.TAGGING,
        DecisionStep.CLONING_CHEMISTRY,
        DecisionStep.BIOSAFETY_TIER,
    ],
)
def test_each_step_has_filterable_candidates(step: DecisionStep) -> None:
    tree, _service, _log = _tree()
    if step.value in {"cargo", "expression", "tagging"}:
        context = _context_through_host(tree)
    else:
        context = _context_with_objective(tree)

    candidates = tree.candidates(step, context)

    assert candidates
    assert all(candidate.step is step for candidate in candidates)
    assert tree.step_definitions[step].free_text_capacity_chars >= 2_000


def test_host_candidates_are_filtered_by_objective() -> None:
    tree, _service, _log = _tree()
    context = tree.new_context("session-1").select(
        DecisionStep.OBJECTIVE,
        "objective.mammalian_expression",
    )

    host_ids = {candidate.id for candidate in tree.candidates(DecisionStep.HOST, context)}

    assert "host.hek293t" in host_ids
    assert "host.ecoli_bl21_de3" not in host_ids


def test_part_candidates_are_filtered_by_selected_host_chassis() -> None:
    tree, _service, _log = _tree()
    context = _context_through_host(tree)

    cargo_ids = {candidate.id for candidate in tree.candidates(DecisionStep.CARGO, context)}
    expression_ids = {
        candidate.id for candidate in tree.candidates(DecisionStep.EXPRESSION, context)
    }
    tag_ids = {candidate.id for candidate in tree.candidates(DecisionStep.TAGGING, context)}

    assert cargo_ids == {"reporter.egfp"}
    assert "promoter.t7" in expression_ids
    assert "promoter.cmv" not in expression_ids
    assert "tag.his6" in tag_ids
    assert "signal.igg" not in tag_ids


def test_query_filter_matches_ids_labels_descriptions_and_tags() -> None:
    tree, _service, _log = _tree()
    context = _context_through_host(tree)

    queried = tree.candidates(DecisionStep.EXPRESSION, context, query="T7")

    assert [candidate.id for candidate in queried] == ["promoter.t7"]


def test_full_flow_emits_design_events_and_compiles() -> None:
    tree, service, log = _tree()
    principal = _user()
    service.create_session(principal, "session-1", project_name="demo")
    context = tree.new_context("session-1")

    selections = {
        DecisionStep.OBJECTIVE: "objective.bacterial_expression",
        DecisionStep.HOST: "host.ecoli_bl21_de3",
        DecisionStep.CARGO: "reporter.egfp",
        DecisionStep.EXPRESSION: "promoter.t7",
        DecisionStep.TAGGING: "tag.his6",
        DecisionStep.CLONING_CHEMISTRY: "chemistry.gibson",
        DecisionStep.BIOSAFETY_TIER: "biosafety.BSL-1",
    }
    for step in DECISION_STEP_ORDER:
        result = tree.advance(
            principal,
            context,
            step,
            selections[step],
            free_text="specialised note" if step is DecisionStep.CARGO else None,
        )
        context = result.context

    draft = tree.compileable_construct(context)
    compiled = tree.compile_current_design(principal, context)
    current = service.open_session(principal, "session-1")

    assert context.is_complete
    assert draft.selected_part_ids == ("reporter.egfp", "promoter.t7", "tag.his6")
    assert draft.biosafety_tier == "BSL-1"
    assert compiled.session.state is SessionState.AWAITING_SCREENING
    assert current.canonical_json() == compiled.session.canonical_json()
    assert [event.event_type for event in log.read_events("session-1")] == [
        "SessionStarted",
        "FreeTextEntered",
        "HostSelected",
        "PartAdded",
        "FreeTextEntered",
        "PartAdded",
        "PartAdded",
        "FreeTextEntered",
        "FreeTextEntered",
        "LLMTranslationConfirmed",
        "DesignCompiled",
    ]


def test_locked_step_cannot_be_changed() -> None:
    tree, _service, _log = _tree()
    context = tree.new_context("session-1").select(
        DecisionStep.OBJECTIVE,
        "objective.bacterial_expression",
    )
    locked = context.lock(DecisionStep.OBJECTIVE)

    with pytest.raises(ValueError, match="locked"):
        locked.select(DecisionStep.OBJECTIVE, "objective.mammalian_expression")


def _tree() -> tuple[DecisionTree, DesignService, InMemoryDesignEventLog]:
    log = InMemoryDesignEventLog()
    service = DesignService(
        design_event_log=log,
        project_store=InMemoryProjectStore(),
        snapshot_store=InMemorySnapshotStore(),
        clock=_clock(),
    )
    return (
        DecisionTree(
            part_catalogue=InMemoryCatalogue(_part_items()),
            host_catalogue=InMemoryCatalogue(_host_items()),
            design_service=service,
        ),
        service,
        log,
    )


def _context_with_objective(tree: DecisionTree) -> DecisionContext:
    return tree.new_context("session-1").select(
        DecisionStep.OBJECTIVE,
        "objective.bacterial_expression",
    )


def _context_through_host(tree: DecisionTree) -> DecisionContext:
    return _context_with_objective(tree).select(DecisionStep.HOST, "host.ecoli_bl21_de3")


def _user() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("institution-1"),
        credentials_verified_at=NOW,
    )


def _clock() -> Callable[[], datetime]:
    counter = 0

    def next_time() -> datetime:
        nonlocal counter
        counter += 1
        return NOW + timedelta(seconds=counter)

    return next_time


def _part_items() -> tuple[Mapping[str, object], ...]:
    citation = {"url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18"}
    return (
        {
            "citation": citation,
            "host_compatibility": ["bacterial", "cell_free"],
            "id": "reporter.egfp",
            "name": "EGFP",
            "role_label": "reporter_cds",
        },
        {
            "citation": citation,
            "host_compatibility": ["mammalian"],
            "id": "reporter.nanoluc_mammalian",
            "name": "NanoLuc mammalian cassette",
            "role_label": "reporter_cds",
        },
        {
            "citation": citation,
            "host_compatibility": ["bacterial"],
            "id": "promoter.t7",
            "name": "T7 promoter",
            "role_label": "promoter",
        },
        {
            "citation": citation,
            "host_compatibility": ["mammalian"],
            "id": "promoter.cmv",
            "name": "CMV promoter",
            "role_label": "promoter",
        },
        {
            "citation": citation,
            "host_compatibility": ["bacterial", "mammalian"],
            "id": "tag.his6",
            "name": "6xHis tag",
            "role_label": "protein_tag",
        },
        {
            "citation": citation,
            "host_compatibility": ["mammalian"],
            "id": "signal.igg",
            "name": "IgG signal peptide",
            "role_label": "signal_peptide",
        },
    )


def _host_items() -> tuple[Mapping[str, object], ...]:
    citation = {"url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18"}
    return (
        {
            "biosafety_tier": "BSL-1",
            "chassis_class": "bacterial",
            "citation": citation,
            "host_roles": ["expression", "protein_expression"],
            "id": "host.ecoli_bl21_de3",
            "name": "E. coli BL21(DE3)",
        },
        {
            "biosafety_tier": "BSL-2",
            "chassis_class": "mammalian",
            "citation": citation,
            "host_roles": ["expression", "transient_expression"],
            "id": "host.hek293t",
            "name": "HEK293T",
        },
    )
