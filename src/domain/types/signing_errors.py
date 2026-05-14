"""
module_id: domain.types.signing_errors
file: src/domain/types/signing_errors.py
task_id: T-314a

Signing verification result and error taxonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")
ErrorT = TypeVar("ErrorT", bound=Exception)


@dataclass(frozen=True)
class Result(Generic[ValueT, ErrorT]):
    success: bool
    value: ValueT | None = None
    error: ErrorT | None = None

    @classmethod
    def ok(cls, value: ValueT) -> Result[ValueT, ErrorT]:
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: ErrorT) -> Result[ValueT, ErrorT]:
        return cls(success=False, error=error)

    def __post_init__(self) -> None:
        if self.success and self.error is not None:
            raise ValueError("successful Result cannot carry an error")
        if not self.success and self.error is None:
            raise ValueError("failed Result requires an error")


class ProfileVerificationError(ValueError):
    """Base class for authorisation-profile verification failures."""


class DecisionRecordVerificationError(ValueError):
    """Base class for decision-record verification failures."""


class SopTemplateVerificationError(ValueError):
    """Base class for SOP-template verification failures."""


class ProfileTamperDetectedError(ProfileVerificationError):
    """Raised when a profile payload or signature no longer matches."""


class SopTemplateTamperDetectedError(SopTemplateVerificationError):
    """Raised when an SOP template payload or signature no longer matches."""


class UnknownKeyVersionError(
    ProfileVerificationError,
    DecisionRecordVerificationError,
    SopTemplateVerificationError,
):
    """Raised when a signature references an unknown key version."""


class RevokedKeyError(
    ProfileVerificationError,
    DecisionRecordVerificationError,
    SopTemplateVerificationError,
):
    """Raised when a signature references a revoked key version."""


class DecisionRecordTamperDetectedError(DecisionRecordVerificationError):
    """Raised when a decision record payload or signature no longer matches."""


class DecisionRecordPrincipalMismatchError(DecisionRecordVerificationError):
    """Raised when a signed decision is bound to the wrong principal."""


ProfileVerificationResult = Result[None, ProfileVerificationError]
DecisionRecordVerificationResult = Result[None, DecisionRecordVerificationError]
SopTemplateVerificationResult = Result[None, SopTemplateVerificationError]
