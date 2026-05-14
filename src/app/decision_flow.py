"""
module_id: app.decision_flow
file: src/app/decision_flow.py
task_id: T-607

Typed decision-tree flow primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType

from domain.events import SessionId

FREE_TEXT_CAPACITY_CHARS = 8_000


class DecisionStep(Enum):
    OBJECTIVE = "objective"
    HOST = "host"
    CARGO = "cargo"
    EXPRESSION = "expression"
    TAGGING = "tagging"
    CLONING_CHEMISTRY = "cloning_chemistry"
    BIOSAFETY_TIER = "biosafety_tier"


DECISION_STEP_ORDER = (
    DecisionStep.OBJECTIVE,
    DecisionStep.HOST,
    DecisionStep.CARGO,
    DecisionStep.EXPRESSION,
    DecisionStep.TAGGING,
    DecisionStep.CLONING_CHEMISTRY,
    DecisionStep.BIOSAFETY_TIER,
)


@dataclass(frozen=True)
class StepDefinition:
    step: DecisionStep
    title: str
    tooltip: str
    free_text_label: str = "Other / specialised - describe your requirement"
    free_text_capacity_chars: int = FREE_TEXT_CAPACITY_CHARS

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("step title cannot be empty")
        if self.free_text_capacity_chars < 2_000:
            raise ValueError("free-text capacity must be at least 2,000 characters")


@dataclass(frozen=True)
class DecisionCandidate:
    id: str
    label: str
    step: DecisionStep
    description: str
    payload_hash: str
    citation_url: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("candidate id cannot be empty")
        if not self.label:
            raise ValueError("candidate label cannot be empty")
        if not self.description:
            raise ValueError("candidate description cannot be empty")
        if not self.payload_hash:
            raise ValueError("candidate payload_hash cannot be empty")


@dataclass(frozen=True)
class FreeTextEntry:
    step: DecisionStep
    text: str

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("free-text entry cannot be empty")
        if len(self.text) > FREE_TEXT_CAPACITY_CHARS:
            raise ValueError(f"free-text entry exceeds {FREE_TEXT_CAPACITY_CHARS} characters")


@dataclass(frozen=True)
class DecisionContext:
    session_id: SessionId
    selections: MappingProxyType[DecisionStep, str] = field(
        default_factory=lambda: MappingProxyType({})
    )
    free_text_entries: tuple[FreeTextEntry, ...] = ()
    locked_steps: frozenset[DecisionStep] = frozenset()

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("session_id cannot be empty")

    def selected(self, step: DecisionStep) -> str | None:
        return self.selections.get(step)

    def select(self, step: DecisionStep, candidate_id: str) -> DecisionContext:
        if step in self.locked_steps and self.selections.get(step) != candidate_id:
            raise ValueError(f"{step.value} is locked")
        if not candidate_id:
            raise ValueError("candidate_id cannot be empty")
        updated = dict(self.selections)
        updated[step] = candidate_id
        return DecisionContext(
            session_id=self.session_id,
            selections=MappingProxyType(updated),
            free_text_entries=self.free_text_entries,
            locked_steps=self.locked_steps,
        )

    def add_free_text(self, step: DecisionStep, text: str) -> DecisionContext:
        return DecisionContext(
            session_id=self.session_id,
            selections=self.selections,
            free_text_entries=(*self.free_text_entries, FreeTextEntry(step=step, text=text)),
            locked_steps=self.locked_steps,
        )

    def lock(self, step: DecisionStep) -> DecisionContext:
        return DecisionContext(
            session_id=self.session_id,
            selections=self.selections,
            free_text_entries=self.free_text_entries,
            locked_steps=self.locked_steps | {step},
        )

    def unlock(self, step: DecisionStep) -> DecisionContext:
        return DecisionContext(
            session_id=self.session_id,
            selections=self.selections,
            free_text_entries=self.free_text_entries,
            locked_steps=self.locked_steps - {step},
        )

    @property
    def next_step(self) -> DecisionStep | None:
        for step in DECISION_STEP_ORDER:
            if step not in self.selections:
                return step
        return None

    @property
    def is_complete(self) -> bool:
        return self.next_step is None


STEP_DEFINITIONS = {
    DecisionStep.OBJECTIVE: StepDefinition(
        step=DecisionStep.OBJECTIVE,
        title="Objective",
        tooltip=(
            "Choose the design intent so later host, cargo, and expression choices are filtered."
        ),
    ),
    DecisionStep.HOST: StepDefinition(
        step=DecisionStep.HOST,
        title="Target Host",
        tooltip="Choose the biological chassis or workflow host for the design context.",
    ),
    DecisionStep.CARGO: StepDefinition(
        step=DecisionStep.CARGO,
        title="Cargo",
        tooltip="Choose the expressed or manipulated sequence element to place in the construct.",
    ),
    DecisionStep.EXPRESSION: StepDefinition(
        step=DecisionStep.EXPRESSION,
        title="Expression",
        tooltip="Choose promoter, induction, and translation-initiation context.",
    ),
    DecisionStep.TAGGING: StepDefinition(
        step=DecisionStep.TAGGING,
        title="Tagging",
        tooltip="Choose localisation, purification, detection, or cleavage tags where needed.",
    ),
    DecisionStep.CLONING_CHEMISTRY: StepDefinition(
        step=DecisionStep.CLONING_CHEMISTRY,
        title="Cloning Chemistry",
        tooltip=(
            "Choose the assembly chemistry that the downstream assembly engine should consider."
        ),
    ),
    DecisionStep.BIOSAFETY_TIER: StepDefinition(
        step=DecisionStep.BIOSAFETY_TIER,
        title="Biosafety Tier",
        tooltip=(
            "Record the declared institutional biosafety context for downstream screening gates."
        ),
    ),
}


__all__ = [
    "DECISION_STEP_ORDER",
    "FREE_TEXT_CAPACITY_CHARS",
    "STEP_DEFINITIONS",
    "DecisionCandidate",
    "DecisionContext",
    "DecisionStep",
    "FreeTextEntry",
    "StepDefinition",
]
