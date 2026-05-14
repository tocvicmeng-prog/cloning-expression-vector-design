"""
module_id: engine.compatibility
file: src/engine/compatibility/__init__.py
task_id: T-504

Role-keyed host/design compatibility checking.
"""

from __future__ import annotations

from typing import NoReturn

from engine.compatibility.engine import (
    CompatibilityChecker,
    CompatibilityIssue,
    CompatibilityReport,
    HostCompatibilityResult,
)
from engine.compatibility.host_constraints import (
    DesignCompatibilityProfile,
    extract_design_compatibility_profile,
)
from engine.compatibility.host_iteration import HostWorkflow, iter_host_contexts
from engine.compatibility.threshold_resolution import (
    HostThresholdProfile,
    resolve_threshold_profile,
)

MODULE_ID = "engine.compatibility"
OWNING_TASKS = ("T-504",)


class PublicApiStub:
    """Historical marker retained for T-203 scaffold compatibility."""


def module_not_implemented() -> NoReturn:
    """Raise for callers that still use the pre-T-504 placeholder sentinel."""
    raise NotImplementedError(f"{MODULE_ID} public API has been replaced by T-504")


__all__ = [
    "CompatibilityChecker",
    "CompatibilityIssue",
    "CompatibilityReport",
    "DesignCompatibilityProfile",
    "HostCompatibilityResult",
    "HostThresholdProfile",
    "HostWorkflow",
    "PublicApiStub",
    "extract_design_compatibility_profile",
    "iter_host_contexts",
    "module_not_implemented",
    "resolve_threshold_profile",
]
