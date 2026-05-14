"""
module_id: interface.audit_service.governance_event_writer
file: src/interface/audit_service/governance_event_writer.py
task_id: T-313b

Minimal governance-event writer owned by the audit service.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from adapter.persistence import JsonlEventLog
from domain.events import AuditServiceAuthenticationFailed, EventStream


class AuditServiceGovernanceEventWriter:
    def __init__(
        self,
        root_dir: str,
        *,
        institution_id: str,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._log = JsonlEventLog(root_dir, expected_stream=EventStream.GOVERNANCE)
        self._institution_id = institution_id
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sequence = 0

    def authentication_failed(self, principal_id: str, reason: str) -> str:
        self._sequence += 1
        event = AuditServiceAuthenticationFailed(
            event_id=f"AuditServiceAuthenticationFailed-{self._sequence:06d}",
            occurred_at_utc=self._clock(),
            actor_id="audit-service",
            institution_id=self._institution_id,
            principal_id=principal_id,
            reason=reason,
        )
        return self._log.append_event(self._institution_id, event)

    def read_events(self) -> tuple[AuditServiceAuthenticationFailed, ...]:
        return tuple(
            event
            for event in self._log.read_events(self._institution_id)
            if isinstance(event, AuditServiceAuthenticationFailed)
        )
