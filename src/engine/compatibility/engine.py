"""
module_id: engine.compatibility.engine
file: src/engine/compatibility/engine.py
task_id: T-504

Pure role-keyed host/design compatibility checker.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from domain.canonicalisation import canonical_sha256
from domain.sequence import Sha256
from domain.types.construct import Construct
from domain.types.enums import ChassisClass, HostRole, SafetyGate, Severity
from domain.types.host import Host
from domain.types.host_compat import HostCompatibilityConstraints
from domain.types.host_context import HostContext
from domain.types.ids import HostId
from engine.compatibility.host_constraints import (
    DesignCompatibilityProfile,
    extract_design_compatibility_profile,
)
from engine.compatibility.host_iteration import iter_host_contexts
from engine.compatibility.threshold_resolution import (
    HostThresholdProfile,
    resolve_threshold_profile,
)
from engine.markers_resolver import MarkersResolver


@dataclass(frozen=True)
class CompatibilityIssue:
    host_id: HostId
    host_role: HostRole
    check_id: str
    severity: Severity
    message: str
    suggested_remediation: str
    threshold_profile: str
    blocks: frozenset[SafetyGate] = frozenset()

    @property
    def blocked_gates(self) -> frozenset[SafetyGate]:
        if self.severity is Severity.HARD:
            return self.blocks
        return frozenset()

    def to_payload(self) -> dict[str, object]:
        return {
            "blocks": sorted(gate.value for gate in self.blocks),
            "check_id": self.check_id,
            "host_id": str(self.host_id),
            "host_role": self.host_role.value,
            "message": self.message,
            "severity": self.severity.value,
            "suggested_remediation": self.suggested_remediation,
            "threshold_profile": self.threshold_profile,
        }


@dataclass(frozen=True)
class HostCompatibilityResult:
    host_id: HostId
    host_role: HostRole
    host_chassis: ChassisClass | None
    issues: tuple[CompatibilityIssue, ...] = ()

    @property
    def passed(self) -> bool:
        return not any(issue.blocked_gates for issue in self.issues)

    def to_payload(self) -> dict[str, object]:
        return {
            "host_chassis": self.host_chassis.value if self.host_chassis else None,
            "host_id": str(self.host_id),
            "host_role": self.host_role.value,
            "issues": [issue.to_payload() for issue in self.issues],
            "passed": self.passed,
        }


@dataclass(frozen=True)
class CompatibilityReport:
    host_results: tuple[HostCompatibilityResult, ...]

    @property
    def issues(self) -> tuple[CompatibilityIssue, ...]:
        return tuple(issue for result in self.host_results for issue in result.issues)

    @property
    def blocked_gates(self) -> frozenset[SafetyGate]:
        return frozenset(gate for issue in self.issues for gate in issue.blocked_gates)

    @property
    def passed(self) -> bool:
        return not self.blocked_gates

    def to_payload(self) -> dict[str, object]:
        return {
            "blocked_gates": sorted(gate.value for gate in self.blocked_gates),
            "host_results": [result.to_payload() for result in self.host_results],
            "passed": self.passed,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


@dataclass(frozen=True)
class CompatibilityChecker:
    host_catalogue: Mapping[HostId, Host]
    constraints: Mapping[HostRole, HostCompatibilityConstraints] = field(default_factory=dict)
    threshold_profiles: Mapping[str, HostThresholdProfile] = field(default_factory=dict)
    threshold_profile: str = "thresholds.default"
    # v0.2 Enrichment Amendment (T-412, ARCHITECTURE.md § 9.2): optional resolver
    # over MarkersCataloguePort. Present-day check() does not consume marker
    # metadata — it only compares marker-id sets against host.compatible_markers —
    # so a None resolver is the documented v0.1.0 baseline behaviour. Phase 5/6
    # MR-55..60 predicate enrichment will resolve marker payloads via this field
    # to surface concentrations, host_genotype_requirement, and citations in
    # error messages and suggested-remediation strings.
    markers_resolver: MarkersResolver | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "host_catalogue", dict(self.host_catalogue))
        object.__setattr__(self, "constraints", dict(self.constraints))
        object.__setattr__(self, "threshold_profiles", dict(self.threshold_profiles))
        if not self.threshold_profile:
            raise ValueError("threshold_profile cannot be empty")
        for role, constraint in self.constraints.items():
            if role is not constraint.role:
                raise ValueError("constraint mapping key must match constraint role")

    def check(
        self,
        construct: Construct,
        hosts: Iterable[HostContext] | None = None,
    ) -> CompatibilityReport:
        profile = extract_design_compatibility_profile(construct)
        results = tuple(
            self._check_host_context(context, profile)
            for context in iter_host_contexts(construct, hosts)
        )
        return CompatibilityReport(host_results=results)

    def _check_host_context(
        self,
        context: HostContext,
        profile: DesignCompatibilityProfile,
    ) -> HostCompatibilityResult:
        threshold_profile = resolve_threshold_profile(
            self.threshold_profiles,
            context,
            self.threshold_profile,
        )
        host = self.host_catalogue.get(context.host_id)
        if host is None:
            return HostCompatibilityResult(
                host_id=context.host_id,
                host_role=context.role,
                host_chassis=None,
                issues=(
                    self._issue(
                        context,
                        threshold_profile,
                        check_id="host_catalogue",
                        message=f"Host {context.host_id} is not present in the host catalogue.",
                        suggested_remediation="Select a host from the active host catalogue.",
                    ),
                ),
            )
        issues = (
            *self._constraint_issues(context, host, profile, threshold_profile),
            *self._part_chassis_issues(context, host, profile, threshold_profile),
        )
        return HostCompatibilityResult(
            host_id=context.host_id,
            host_role=context.role,
            host_chassis=host.chassis,
            issues=issues,
        )

    def _constraint_issues(
        self,
        context: HostContext,
        host: Host,
        profile: DesignCompatibilityProfile,
        threshold_profile: HostThresholdProfile,
    ) -> tuple[CompatibilityIssue, ...]:
        constraint = self.constraints.get(context.role)
        if constraint is None:
            return ()
        issues: list[CompatibilityIssue] = []
        if host.chassis not in constraint.allowed_chassis:
            allowed = ", ".join(sorted(chassis.value for chassis in constraint.allowed_chassis))
            issues.append(
                self._issue(
                    context,
                    threshold_profile,
                    check_id="chassis_role",
                    message=(
                        f"{host.name} is {host.chassis.value}, "
                        f"not allowed for {context.role.value}."
                    ),
                    suggested_remediation=f"Use a host role backed by one of: {allowed}.",
                )
            )
        incompatible_origins = (
            profile.origins - host.compatible_origins if host.compatible_origins else frozenset()
        )
        missing_required_origins = constraint.required_origins - profile.origins
        for origin in sorted(incompatible_origins | missing_required_origins):
            issues.append(
                self._issue(
                    context,
                    threshold_profile,
                    check_id="origin_compatibility",
                    message=(
                        f"Origin {origin} is not compatible with "
                        f"{host.name} as {context.role.value}."
                    ),
                    suggested_remediation="Choose an origin supported by the host role.",
                )
            )
        incompatible_markers = (
            profile.markers - host.compatible_markers if host.compatible_markers else frozenset()
        )
        forbidden_markers = profile.markers & constraint.forbidden_markers
        for marker in sorted(incompatible_markers | forbidden_markers):
            issues.append(
                self._issue(
                    context,
                    threshold_profile,
                    check_id="marker_compatibility",
                    message=(
                        f"Marker {marker} is not compatible with "
                        f"{host.name} as {context.role.value}."
                    ),
                    suggested_remediation=(
                        "Choose a selectable marker valid for every required host role."
                    ),
                )
            )
        return tuple(issues)

    def _part_chassis_issues(
        self,
        context: HostContext,
        host: Host,
        profile: DesignCompatibilityProfile,
        threshold_profile: HostThresholdProfile,
    ) -> tuple[CompatibilityIssue, ...]:
        return tuple(
            self._issue(
                context,
                threshold_profile,
                check_id="part_chassis",
                message=f"Part {part.id} does not declare compatibility with {host.chassis.value}.",
                suggested_remediation="Select a part variant compatible with the host chassis.",
            )
            for part in profile.parts
            if part.host_compatibility and host.chassis not in part.host_compatibility
        )

    def _issue(
        self,
        context: HostContext,
        threshold_profile: HostThresholdProfile,
        *,
        check_id: str,
        message: str,
        suggested_remediation: str,
    ) -> CompatibilityIssue:
        severity = threshold_profile.severity_for(check_id)
        return CompatibilityIssue(
            host_id=context.host_id,
            host_role=context.role,
            check_id=check_id,
            severity=severity,
            message=message,
            suggested_remediation=suggested_remediation,
            threshold_profile=threshold_profile.profile_id,
            blocks=threshold_profile.blocks_for(check_id, severity),
        )


__all__ = [
    "CompatibilityChecker",
    "CompatibilityIssue",
    "CompatibilityReport",
    "HostCompatibilityResult",
]
