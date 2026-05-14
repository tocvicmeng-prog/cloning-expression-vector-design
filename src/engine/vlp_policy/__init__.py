"""
module_id: engine.vlp_policy
file: src/engine/vlp_policy/__init__.py
task_id: T-807

Public VLP/AAV/lentiviral policy API.
"""

from __future__ import annotations

from engine.vlp_policy.policy import (
    VlpPolicyEngine,
    VlpPolicyFinding,
    VlpPolicyReport,
    VlpPolicyRequest,
    VlpPolicySeverity,
    evaluate_vlp_policy,
)
from engine.vlp_policy.system_classes import (
    MS_RULE_IDS,
    SYSTEM_CLASS_CAPACITY_NT,
    SYSTEM_CLASS_RISK_TAGS,
    VlpSystemClass,
)

MODULE_ID = "engine.vlp_policy"
OWNING_TASKS = ("T-807",)

__all__ = [
    "MS_RULE_IDS",
    "SYSTEM_CLASS_CAPACITY_NT",
    "SYSTEM_CLASS_RISK_TAGS",
    "VlpPolicyEngine",
    "VlpPolicyFinding",
    "VlpPolicyReport",
    "VlpPolicyRequest",
    "VlpPolicySeverity",
    "VlpSystemClass",
    "evaluate_vlp_policy",
]
