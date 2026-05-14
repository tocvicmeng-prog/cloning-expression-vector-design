"""
module_id: engine.session.state_machine
file: src/engine/session/state_machine.py
task_id: T-309

Pure design-session state machine.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from enum import Enum

from domain.events import (
    DesignCompiled,
    DesignEvent,
    FreeTextEntered,
    HostSelected,
    LLMTranslationConfirmed,
    LLMTranslationProposed,
    OperationalProtocolAuthorised,
    OverrideJustified,
    PartAdded,
    RuleAcknowledged,
    ScreeningCompleted,
    SessionForked,
    SessionId,
    SessionStarted,
    SopRendered,
)
from domain.sequence import Sha256


class SessionState(Enum):
    EMPTY = "EMPTY"
    COLLECTING = "COLLECTING"
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    HARD_FAIL = "HARD-FAIL"
    SOFT_WARN = "SOFT-WARN"
    ALL_PASS = "ALL-PASS"
    ACKNOWLEDGED_WARN = "ACKNOWLEDGED_WARN"
    COMPILING = "COMPILING"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    AWAITING_SCREENING = "AWAITING_SCREENING"
    SCREENING = "SCREENING"
    HIT = "HIT"
    WATCHLIST = "WATCHLIST"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    CLEAR = "CLEAR"
    AWAITING_REVIEWER_SIGNOFF = "AWAITING_REVIEWER_SIGNOFF"
    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
    AWAITING_SOP_RENDER = "AWAITING_SOP_RENDER"
    READY_TO_EXPORT = "READY_TO_EXPORT"
    EXPORTED = "EXPORTED"
    BLOCKED_BY_HIT = "BLOCKED_BY_HIT"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    BLOCKED_BY_UNSUPPORTED_TIER = "BLOCKED_BY_UNSUPPORTED_TIER"


TERMINAL_STATES = frozenset(
    {
        SessionState.EXPORTED,
        SessionState.BLOCKED_BY_HIT,
        SessionState.BLOCKED_BY_POLICY,
        SessionState.BLOCKED_BY_UNSUPPORTED_TIER,
    }
)


class SessionTransitionError(ValueError):
    """Raised when an event cannot be applied to the current session state."""


@dataclass(frozen=True)
class DesignSession:
    session_id: SessionId
    state: SessionState = SessionState.EMPTY
    project_name: str | None = None
    part_ids: tuple[str, ...] = ()
    host_ids: tuple[str, ...] = ()
    free_text_entries: tuple[str, ...] = ()
    structured_translation_hashes: tuple[str, ...] = ()
    acknowledged_rule_ids: tuple[str, ...] = ()
    override_ids: tuple[str, ...] = ()
    construct_id: str | None = None
    construct_checksum: str | None = None
    design_plan_hash: str | None = None
    screening_batch_id: str | None = None
    screening_verdict: str | None = None
    authorisation_profile_id: str | None = None
    decision_record_hash: str | None = None
    sop_bundle_hash: str | None = None
    lineage: tuple[SessionId, ...] = ()
    applied_event_ids: tuple[str, ...] = ()
    derivation_environment_hash: Sha256 | None = None
    gate_verdicts: tuple[tuple[str, str, str], ...] = ()
    _event_fingerprints: tuple[tuple[str, str], ...] = field(default=(), repr=False, compare=False)

    def apply(self, event: DesignEvent) -> DesignSession:
        if event.event_id in self.applied_event_ids:
            return self._apply_duplicate(event)
        if self.session_id and event.session_id != self.session_id:
            raise SessionTransitionError("event session_id does not match design session")

        updated = self._apply_new_event(event)
        return updated._with_event(event)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "acknowledged_rule_ids": list(self.acknowledged_rule_ids),
            "applied_event_ids": list(self.applied_event_ids),
            "authorisation_profile_id": self.authorisation_profile_id,
            "construct_checksum": self.construct_checksum,
            "construct_id": self.construct_id,
            "decision_record_hash": self.decision_record_hash,
            "derivation_environment_hash": None
            if self.derivation_environment_hash is None
            else str(self.derivation_environment_hash),
            "free_text_entries": list(self.free_text_entries),
            "gate_verdicts": [list(item) for item in self.gate_verdicts],
            "host_ids": list(self.host_ids),
            "lineage": list(self.lineage),
            "override_ids": list(self.override_ids),
            "part_ids": list(self.part_ids),
            "project_name": self.project_name,
            "screening_batch_id": self.screening_batch_id,
            "screening_verdict": self.screening_verdict,
            "session_id": self.session_id,
            "sop_bundle_hash": self.sop_bundle_hash,
            "state": self.state.value,
            "structured_translation_hashes": list(self.structured_translation_hashes),
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True, separators=(",", ":"))

    def _apply_new_event(self, event: DesignEvent) -> DesignSession:
        if isinstance(event, SessionStarted):
            return self._start(event)
        if isinstance(event, PartAdded):
            self._require_state(event, SessionState.COLLECTING, SessionState.DRAFT)
            return replace(
                self, part_ids=(*self.part_ids, event.part_id), state=SessionState.COLLECTING
            )
        if isinstance(event, HostSelected):
            self._require_state(event, SessionState.COLLECTING, SessionState.DRAFT)
            return replace(
                self, host_ids=(*self.host_ids, event.host_id), state=SessionState.COLLECTING
            )
        if isinstance(event, FreeTextEntered):
            self._require_state(event, SessionState.COLLECTING, SessionState.DRAFT)
            return replace(
                self,
                free_text_entries=(*self.free_text_entries, event.text),
                state=SessionState.COLLECTING,
            )
        if isinstance(event, LLMTranslationProposed):
            self._require_state(event, SessionState.COLLECTING, SessionState.DRAFT)
            return replace(
                self,
                structured_translation_hashes=(
                    *self.structured_translation_hashes,
                    _payload_fingerprint(event.structured),
                ),
                state=SessionState.COLLECTING,
            )
        if isinstance(event, LLMTranslationConfirmed):
            self._require_state(event, SessionState.COLLECTING, SessionState.DRAFT)
            return replace(
                self,
                structured_translation_hashes=(
                    *self.structured_translation_hashes,
                    _payload_fingerprint(event.structured),
                ),
                state=SessionState.DRAFT,
            )
        if isinstance(event, RuleAcknowledged):
            self._require_state(event, SessionState.DRAFT, SessionState.SOFT_WARN)
            return replace(
                self,
                acknowledged_rule_ids=(*self.acknowledged_rule_ids, event.rule_id),
                state=SessionState.ACKNOWLEDGED_WARN,
            )
        if isinstance(event, OverrideJustified):
            self._require_state(event, SessionState.DRAFT, SessionState.SOFT_WARN)
            return replace(
                self,
                override_ids=(*self.override_ids, event.override_id),
                state=SessionState.ACKNOWLEDGED_WARN,
            )
        if isinstance(event, DesignCompiled):
            self._require_state(
                event,
                SessionState.DRAFT,
                SessionState.ACKNOWLEDGED_WARN,
                SessionState.ALL_PASS,
                SessionState.READY_WITH_WARNINGS,
            )
            return replace(
                self,
                construct_id=event.construct_id,
                construct_checksum=event.construct_checksum,
                design_plan_hash=event.design_plan_hash,
                state=SessionState.AWAITING_SCREENING,
            )
        if isinstance(event, ScreeningCompleted):
            self._require_state(event, SessionState.AWAITING_SCREENING, SessionState.SCREENING)
            return self._apply_screening(event)
        if isinstance(event, OperationalProtocolAuthorised):
            self._require_state(
                event,
                SessionState.AWAITING_AUTHORISATION,
                SessionState.AWAITING_REVIEWER_SIGNOFF,
            )
            return replace(
                self,
                authorisation_profile_id=event.profile_id,
                decision_record_hash=event.decision_record_hash,
                state=SessionState.AWAITING_SOP_RENDER,
            )
        if isinstance(event, SopRendered):
            self._require_state(event, SessionState.AWAITING_SOP_RENDER)
            return replace(
                self, sop_bundle_hash=event.sop_bundle_hash, state=SessionState.READY_TO_EXPORT
            )
        if isinstance(event, SessionForked):
            self._require_not_terminal(event)
            return replace(self, lineage=event.lineage)
        raise SessionTransitionError(f"unsupported design event: {event.event_type}")

    def _start(self, event: SessionStarted) -> DesignSession:
        if self.state is not SessionState.EMPTY:
            raise SessionTransitionError("SessionStarted can only be applied to EMPTY sessions")
        return replace(
            self,
            session_id=event.session_id,
            project_name=event.project_name,
            state=SessionState.COLLECTING,
        )

    def _apply_screening(self, event: ScreeningCompleted) -> DesignSession:
        verdict = _payload_value(event.verdict_payload, "verdict").upper()
        next_state = {
            "HIT": SessionState.BLOCKED_BY_HIT,
            "WATCHLIST": SessionState.AWAITING_REVIEWER_SIGNOFF,
            "MANUAL_REVIEW_REQUIRED": SessionState.AWAITING_REVIEWER_SIGNOFF,
            "UNAVAILABLE": SessionState.BLOCKED_BY_POLICY,
            "NOT_APPLICABLE": SessionState.AWAITING_AUTHORISATION,
            "CLEAR": SessionState.AWAITING_AUTHORISATION,
        }.get(verdict)
        if next_state is None:
            raise SessionTransitionError(f"unsupported screening verdict: {verdict}")
        return replace(
            self,
            screening_batch_id=event.batch_id,
            screening_verdict=verdict,
            state=next_state,
        )

    def _with_event(self, event: DesignEvent) -> DesignSession:
        return replace(
            self,
            applied_event_ids=(*self.applied_event_ids, event.event_id),
            _event_fingerprints=(
                *self._event_fingerprints,
                (event.event_id, event.canonical_json()),
            ),
        )

    def _apply_duplicate(self, event: DesignEvent) -> DesignSession:
        for event_id, fingerprint in self._event_fingerprints:
            if event_id == event.event_id and fingerprint == event.canonical_json():
                return self
        raise SessionTransitionError(f"conflicting duplicate event_id: {event.event_id}")

    def _require_state(self, event: DesignEvent, *allowed: SessionState) -> None:
        if self.state not in allowed:
            allowed_names = ", ".join(state.value for state in allowed)
            raise SessionTransitionError(
                f"{event.event_type} cannot be applied in {self.state.value}; "
                f"expected {allowed_names}"
            )

    def _require_not_terminal(self, event: DesignEvent) -> None:
        if self.state in TERMINAL_STATES:
            raise SessionTransitionError(
                f"{event.event_type} cannot be applied after terminal state {self.state.value}"
            )


def empty_session(session_id: SessionId) -> DesignSession:
    return DesignSession(session_id=session_id)


def _payload_value(payload: tuple[tuple[str, str], ...], key: str) -> str:
    for payload_key, value in payload:
        if payload_key == key:
            return value
    raise SessionTransitionError(f"payload is missing required key: {key}")


def _payload_fingerprint(payload: tuple[tuple[str, str], ...]) -> str:
    return json.dumps(sorted(payload), separators=(",", ":"))
