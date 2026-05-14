"""
module_id: domain.types.derivation.policies
file: src/domain/types/derivation/policies.py
task_id: T-307

Policy enums captured by DerivationEnvironmentV14.
"""

from __future__ import annotations

from enum import Enum


class ScreeningScope(Enum):
    ASSEMBLED_PRODUCT = "assembled_product"
    PARTS_AND_ASSEMBLED_PRODUCT = "parts_and_assembled_product"
    FULL_LIBRARY = "full_library"


class ExportProfile(Enum):
    INTERNAL_AUDIT = "internal_audit"
    COLLABORATOR = "collaborator"
    VENDOR = "vendor"
    PUBLICATION_SUPPLEMENT = "publication_supplement"


class PrivacyClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    REGULATED = "regulated"
