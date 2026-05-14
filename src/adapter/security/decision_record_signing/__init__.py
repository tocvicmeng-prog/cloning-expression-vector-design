"""
module_id: adapter.security.decision_record_signing
file: src/adapter/security/decision_record_signing/__init__.py
task_id: T-314b

Production decision-record signing adapters.
"""

from __future__ import annotations

from adapter.security.decision_record_signing.per_principal_signer import (
    PerPrincipalDecisionRecordSigner,
)
from adapter.security.decision_record_signing.per_principal_verifier import (
    PerPrincipalDecisionRecordVerifier,
)
from adapter.security.decision_record_signing.serialization import (
    signed_decision_from_json,
    signed_decision_to_json,
)

__all__ = [
    "PerPrincipalDecisionRecordSigner",
    "PerPrincipalDecisionRecordVerifier",
    "signed_decision_from_json",
    "signed_decision_to_json",
]
