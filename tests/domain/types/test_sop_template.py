"""
module_id: tests.domain.types.test_sop_template
file: tests/domain/types/test_sop_template.py
task_id: T-316a
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from domain.security import PrincipalId
from domain.sequence import Sha256
from domain.types.derivation import Semver, SopTemplateId
from domain.types.sop_template import (
    SopTemplate,
    SopTemplateRevocation,
    SopTemplateSignature,
    SopTemplateVersion,
)
from tests.fakes.sop_template.fixtures import admin_principal, unsigned_template
from tests.fakes.sop_template.signer import FakeSopTemplateSigner

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def test_sop_template_hash_is_stable_and_signature_bound() -> None:
    template = unsigned_template()
    signature = FakeSopTemplateSigner().sign(template, admin_principal())
    signed = replace(template, signature=signature)

    assert signed.content_hash() == template.content_hash()
    with pytest.raises(ValueError, match="signature content hash"):
        replace(
            signed,
            content_markdown="tampered",
        )


def test_sop_template_value_objects_validate_required_fields() -> None:
    template = unsigned_template()
    signature = FakeSopTemplateSigner().sign(template, admin_principal())
    assert SopTemplateVersion(
        template_id=template.template_id,
        version=template.version,
        content_hash=template.content_hash(),
        created_at_utc=NOW,
    )
    assert SopTemplateRevocation(
        template_id=template.template_id,
        version=template.version,
        revoked_by_principal_id=PrincipalId("admin-1"),
        revoked_at_utc=NOW,
        reason="superseded",
    )

    with pytest.raises(ValueError, match="template_id"):
        SopTemplate(
            template_id=SopTemplateId(""),
            version=Semver("1.0.0"),
            name="bad",
            description="bad",
            content_markdown="bad",
            hazard_notes=(),
            required_approval_gate="gate",
        )
    with pytest.raises(ValueError, match="signature_bytes"):
        SopTemplateSignature(
            template_content_hash=Sha256("sha256:template"),
            signature_bytes=b"",
            signing_key_version=signature.signing_key_version,
            signed_at_utc=NOW,
        )
