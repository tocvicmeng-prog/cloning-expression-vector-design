"""
module_id: engine.compatibility.threshold_resolution
file: src/engine/compatibility/threshold_resolution.py
task_id: T-504

Host-role-aware threshold profile resolution.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from domain.types.enums import SafetyGate, Severity
from domain.types.host_context import HostContext


@dataclass(frozen=True)
class HostThresholdProfile:
    profile_id: str
    default_severity: Severity = Severity.HARD
    severity_overrides: Mapping[str, Severity] = field(default_factory=dict)
    block_overrides: Mapping[str, frozenset[SafetyGate]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError("threshold profile id cannot be empty")
        object.__setattr__(self, "severity_overrides", dict(self.severity_overrides))
        object.__setattr__(self, "block_overrides", dict(self.block_overrides))

    def severity_for(self, check_id: str) -> Severity:
        return self.severity_overrides.get(check_id, self.default_severity)

    def blocks_for(self, check_id: str, severity: Severity) -> frozenset[SafetyGate]:
        if check_id in self.block_overrides:
            return self.block_overrides[check_id]
        if severity is Severity.HARD:
            return frozenset({SafetyGate.COMPILE})
        return frozenset()


def resolve_threshold_profile(
    profiles: Mapping[str, HostThresholdProfile],
    context: HostContext,
    requested_profile: str,
) -> HostThresholdProfile:
    candidates = (
        f"{requested_profile}:{context.role.value}:{context.host_id}",
        f"{requested_profile}:{context.role.value}",
        requested_profile,
    )
    for candidate in candidates:
        profile = profiles.get(candidate)
        if profile is not None:
            return profile
    return HostThresholdProfile(profile_id=requested_profile)


__all__ = [
    "HostThresholdProfile",
    "resolve_threshold_profile",
]
