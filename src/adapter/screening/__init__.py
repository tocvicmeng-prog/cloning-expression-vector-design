"""
module_id: adapter.screening
file: src/adapter/screening/__init__.py
task_id: T-1002

Screening adapter package.
"""

from __future__ import annotations

from adapter.screening.base import (
    BaseScreeningAdapter,
    BatchScreeningOutcome,
    NotApplicableReason,
    ScreeningAdapterFailureClass,
    ScreeningError,
    ScreeningProviderPolicy,
    ScreeningRequest,
    ScreeningResult,
    ScreeningScope,
    ScreeningTrustPolicy,
    ScreeningVerdict,
    load_screening_trust_policy,
)
from adapter.screening.ibbis import IbbisAdapter
from adapter.screening.igsc import IgscAdapter
from adapter.screening.internal_blacklist import InternalBlacklistAdapter
from adapter.screening.securedna import SecureDnaAdapter

__all__ = [
    "BaseScreeningAdapter",
    "BatchScreeningOutcome",
    "IbbisAdapter",
    "IgscAdapter",
    "InternalBlacklistAdapter",
    "NotApplicableReason",
    "ScreeningAdapterFailureClass",
    "ScreeningError",
    "ScreeningProviderPolicy",
    "ScreeningRequest",
    "ScreeningResult",
    "ScreeningScope",
    "ScreeningTrustPolicy",
    "ScreeningVerdict",
    "SecureDnaAdapter",
    "load_screening_trust_policy",
]
