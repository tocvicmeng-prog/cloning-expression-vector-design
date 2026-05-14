"""
module_id: domain.types.enums
file: src/domain/types/enums.py
task_id: T-303

Domain enums used by T-303 core entities.
"""

from __future__ import annotations

from enum import Enum


class BiosafetyTier(Enum):
    BSL_1 = "BSL-1"
    BSL_2 = "BSL-2"
    BSL_2_PLUS = "BSL-2+"
    BSL_3 = "BSL-3"
    BSL_4 = "BSL-4"


class DownstreamUse(Enum):
    CLONING = "cloning"
    EXPRESSION = "expression"
    SCREENING_ASSAY = "screening_assay"
    VLP_OR_PHAGE_DISPLAY = "vlp_or_phage_display"
    OTHER = "other"


class HostRole(Enum):
    CLONING_PROPAGATION = "cloning_propagation"
    ASSEMBLY = "assembly"
    DELIVERY = "delivery"
    PRODUCER = "producer"
    EXPRESSION = "expression"
    TARGET = "target"
    SCREENING_ASSAY = "screening_assay"
    STORAGE = "storage"


class ChassisClass(Enum):
    BACTERIAL = "bacterial"
    YEAST = "yeast"
    PLANT = "plant"
    MAMMALIAN = "mammalian"
    INSECT = "insect"
    CELL_FREE = "cell_free"
    VIRAL_OR_PHAGE = "viral_or_phage"


class ModuleLayer(Enum):
    PROPAGATION = "propagation"
    ASSEMBLY = "assembly"
    EXPRESSION = "expression"
    CARGO = "cargo"
    TERMINATION = "termination"
    METADATA = "metadata"


class SlotKind(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    REPEATABLE = "repeatable"


class AssemblyCapability(Enum):
    SCARLESS = "scarless"
    ORDERED_MULTI_FRAGMENT = "ordered_multi_fragment"
    COMBINATORIAL = "combinatorial"
    LONG_FRAGMENT = "long_fragment"
    IN_VIVO = "in_vivo"


class Severity(Enum):
    HARD = "HARD"
    SOFT = "SOFT"
    INFO = "INFO"


class SeverityPolicy(Enum):
    BLOCK = "block"
    WARN_ACKNOWLEDGE = "warn_acknowledge"
    REPORT_ONLY = "report_only"


class SafetyGate(Enum):
    COMPILE = "BlockCompile"
    EXPORT = "BlockExport"
    VENDOR_SUBMISSION = "BlockVendorSubmission"
    OPERATIONAL_PROTOCOL = "BlockOperationalProtocol"


class ContextScope(Enum):
    CONSTRUCT = "construct"
    HOST_CONTEXT = "host_context"
    ASSEMBLY_PLAN = "assembly_plan"
    SCREENING = "screening"
