"""
module_id: adapter.security.sop_template_signing.serialization
file: src/adapter/security/sop_template_signing/serialization.py
task_id: T-316c

JSON helpers for signed SOP-template offline verification.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from domain.security.identifiers import KeyVersionId
from domain.sequence import Sha256
from domain.types.derivation import Semver, SopTemplateId
from domain.types.sop_template import SopTemplate, SopTemplateSignature


def sop_template_to_json(template: SopTemplate) -> str:
    signature = template.signature
    return json.dumps(
        {
            "content_markdown": template.content_markdown,
            "description": template.description,
            "hazard_notes": list(template.hazard_notes),
            "name": template.name,
            "required_approval_gate": template.required_approval_gate,
            "signature": None
            if signature is None
            else {
                "signature_bytes_hex": signature.signature_bytes.hex(),
                "signed_at_utc": _datetime_to_json(signature.signed_at_utc),
                "signing_key_version": str(signature.signing_key_version),
                "template_content_hash": str(signature.template_content_hash),
            },
            "template_id": str(template.template_id),
            "version": str(template.version),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def sop_template_from_json(payload: str) -> SopTemplate:
    data = _expect_dict(json.loads(payload), "SOP template")
    signature_data = data.get("signature")
    signature = None if signature_data is None else _signature_from_json(signature_data)
    return SopTemplate(
        template_id=SopTemplateId(_expect_str(data, "template_id")),
        version=Semver(_expect_str(data, "version")),
        name=_expect_str(data, "name"),
        description=_expect_str(data, "description"),
        content_markdown=_expect_str(data, "content_markdown"),
        hazard_notes=tuple(
            _expect_str(item, "hazard_notes") for item in _expect_list(data, "hazard_notes")
        ),
        required_approval_gate=_expect_str(data, "required_approval_gate"),
        signature=signature,
    )


def _signature_from_json(raw: object) -> SopTemplateSignature:
    data = _expect_dict(raw, "signature")
    return SopTemplateSignature(
        template_content_hash=Sha256(_expect_str(data, "template_content_hash")),
        signature_bytes=bytes.fromhex(_expect_str(data, "signature_bytes_hex")),
        signing_key_version=KeyVersionId(_expect_str(data, "signing_key_version")),
        signed_at_utc=_parse_datetime(_expect_str(data, "signed_at_utc")),
    )


def _expect_dict(raw: object, field_name: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise TypeError(f"{field_name} must be a JSON object")
    return dict(raw)


def _expect_list(data: dict[str, object], key: str) -> list[object]:
    value = data.get(key)
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list")
    return value


def _expect_str(data: dict[str, object] | object, key: str) -> str:
    value = data.get(key) if isinstance(data, dict) else data
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
