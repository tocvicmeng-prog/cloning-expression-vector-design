"""
module_id: tests.domain.security
file: tests/domain/security/test_principals.py
task_id: T-304
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    DeveloperPrincipal,
    InstitutionId,
    PrincipalId,
    ReviewerPrincipal,
    SecurityRole,
    UserPrincipal,
)

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def test_security_role_inheritance_is_one_way() -> None:
    user = UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )
    reviewer = ReviewerPrincipal(
        id=PrincipalId("reviewer-1"),
        role=SecurityRole.REVIEWER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )
    admin = AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )

    assert not user.can_act_as(SecurityRole.ADMINISTRATOR)
    assert admin.can_act_as(SecurityRole.REVIEWER)
    assert not reviewer.can_act_as(SecurityRole.ADMINISTRATOR)


def test_principal_subclasses_reject_wrong_security_role() -> None:
    with pytest.raises(ValueError, match="UserPrincipal"):
        UserPrincipal(
            id=PrincipalId("user-1"),
            role=SecurityRole.REVIEWER,
            institution=InstitutionId("inst"),
            credentials_verified_at=NOW,
        )


def test_developer_bootstrap_authority_requires_bootstrap_claim_and_unexpired_token() -> None:
    developer = DeveloperPrincipal(
        id=PrincipalId("dev-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("system"),
        credentials_verified_at=NOW,
    )
    bootstrap = DeveloperBootstrapPrincipal(
        id=PrincipalId("dev-bootstrap"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("system"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    expired = DeveloperBootstrapPrincipal(
        id=PrincipalId("dev-expired"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("system"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=datetime.now(UTC) - timedelta(hours=1),
    )

    assert not developer.has_bootstrap_authority
    assert bootstrap.has_bootstrap_authority
    assert not expired.has_bootstrap_authority


def test_principal_timestamps_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        UserPrincipal(
            id=PrincipalId("user-1"),
            role=SecurityRole.USER,
            institution=InstitutionId("inst"),
            credentials_verified_at=datetime(2026, 5, 14),
        )
