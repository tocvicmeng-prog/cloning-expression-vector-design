"""
module_id: engine.vlp_policy.system_classes
file: src/engine/vlp_policy/system_classes.py
task_id: T-807

System-class boundaries for non-operational VLP and viral-vector policy checks.
"""

from __future__ import annotations

from enum import Enum


class VlpSystemClass(Enum):
    MS2_RNA_DISPLAY = "ms2_rna_display"
    PHAGE_DERIVED_VLP = "phage_derived_vlp"
    AAV = "aav"
    LENTIVIRAL = "lentiviral"


SYSTEM_CLASS_CAPACITY_NT: dict[VlpSystemClass, int] = {
    VlpSystemClass.MS2_RNA_DISPLAY: 4000,
    VlpSystemClass.PHAGE_DERIVED_VLP: 4000,
    VlpSystemClass.AAV: 4700,
    VlpSystemClass.LENTIVIRAL: 9000,
}

SYSTEM_CLASS_RISK_TAGS: dict[VlpSystemClass, tuple[str, ...]] = {
    VlpSystemClass.MS2_RNA_DISPLAY: ("MS2", "VLP", "delivery_vehicle"),
    VlpSystemClass.PHAGE_DERIVED_VLP: ("VLP", "phage_derived_vlp", "delivery_vehicle"),
    VlpSystemClass.AAV: ("AAV", "viral_vector", "packaging", "producer_host"),
    VlpSystemClass.LENTIVIRAL: ("lentiviral", "viral_vector", "packaging", "producer_host"),
}

MS_RULE_IDS = frozenset(
    {
        "MS-01",
        "MS-02",
        "MS-03",
        "MS-04",
        "MS-05",
        "MS-06",
        "MS-07",
    }
)


def normalise_token(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


__all__ = [
    "MS_RULE_IDS",
    "SYSTEM_CLASS_CAPACITY_NT",
    "SYSTEM_CLASS_RISK_TAGS",
    "VlpSystemClass",
    "normalise_token",
]
