"""
module_id: domain.types.sop_protected.hazard
file: src/domain/types/sop_protected/hazard.py
task_id: T-306
"""

from __future__ import annotations

from enum import Enum


class HazardClass(Enum):
    BSL1 = "BSL-1"
    BSL2 = "BSL-2"
    BSL2_PLUS = "BSL-2+"
    BSL3 = "BSL-3"
    CHEMICAL_LOW = "chem-low"
    CHEMICAL_HIGH = "chem-high"
