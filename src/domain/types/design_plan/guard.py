"""
module_id: domain.types.design_plan.guard
file: src/domain/types/design_plan/guard.py
task_id: T-306

Runtime guard preventing SOP-protected values from entering non-operational plans.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass

SOP_PROTECTED_MODULE_PREFIX = "domain.types.sop_protected"


def reject_sop_protected_values(value: object) -> None:
    if _contains_sop_protected_value(value):
        raise TypeError("non-operational design artefacts cannot contain sop_protected values")


def _contains_sop_protected_value(value: object) -> bool:
    if value is None or isinstance(value, str | int | float | bool | bytes):
        return False
    if value.__class__.__module__.startswith(SOP_PROTECTED_MODULE_PREFIX):
        return True
    if isinstance(value, tuple | list | frozenset | set):
        return any(_contains_sop_protected_value(item) for item in value)
    if isinstance(value, dict):
        return any(
            _contains_sop_protected_value(key) or _contains_sop_protected_value(item)
            for key, item in value.items()
        )
    if is_dataclass(value) and not isinstance(value, type):
        return any(
            _contains_sop_protected_value(getattr(value, field.name)) for field in fields(value)
        )
    return False
