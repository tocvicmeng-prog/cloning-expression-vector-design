"""
module_id: adapter.security.sop_template_signing
file: src/adapter/security/sop_template_signing/__init__.py
task_id: T-316c

Production SOP-template signing adapters.
"""

from __future__ import annotations

from adapter.security.sop_template_signing.institutional_signer import (
    Ed25519InstitutionalSopTemplateSigner,
)
from adapter.security.sop_template_signing.institutional_verifier import (
    Ed25519InstitutionalSopTemplateVerifier,
)
from adapter.security.sop_template_signing.serialization import (
    sop_template_from_json,
    sop_template_to_json,
)

__all__ = [
    "Ed25519InstitutionalSopTemplateSigner",
    "Ed25519InstitutionalSopTemplateVerifier",
    "sop_template_from_json",
    "sop_template_to_json",
]
