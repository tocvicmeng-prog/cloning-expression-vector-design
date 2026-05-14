"""
module_id: tests.ports
file: tests/ports/test_port_inventory.py
task_id: T-203
"""

from __future__ import annotations

import inspect
from pathlib import Path

import yaml  # type: ignore[import-untyped]

import domain.ports as ports

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_METHODS = {
    "AuthorisationReadPort": {"get", "read_own_profile", "list_for_admin"},
    "AuthorisationAdminWritePort": {"write_mint", "write_modify", "write_revoke"},
    "AuthorisationBootstrapPort": {"bootstrap_initial_admin"},
    "AuditKeyProvider": {
        "mac",
        "verify",
        "verify_with_archived",
        "rotate",
        "current_key_version",
    },
    "AuditAppendPort": {"append"},
    "AdminAuditAppendPort": {"append"},
    "AdminServiceClientPort": {"dispatch"},
    "AuthorisationProfileSigner": {"sign"},
    "AuthorisationProfileVerifier": {"verify"},
    "DecisionRecordSigner": {"sign"},
    "DecisionRecordVerifier": {"verify"},
    "SopTemplateReadPort": {"get_template", "list_templates"},
    "SopTemplateAdminWritePort": {"write_mint", "write_modify", "write_revoke"},
    "SopTemplateBootstrapPort": {"bootstrap_initial_templates"},
    "SopTemplateSigner": {"sign"},
    "SopTemplateVerifier": {"verify"},
    "ReviewQueueStore": {"add", "list_pending", "get"},
    "ReviewQueueAdminPort": {"resolve"},
}

READ_METHODS = {"get", "read_own_profile", "list_for_admin", "list_templates", "read_entry"}
ADMIN_WRITE_PORTS = {
    "AdminAuditAppendPort",
    "AuthorisationAdminWritePort",
    "SopTemplateAdminWritePort",
    "ReviewQueueAdminPort",
}


def _manifest_port_names() -> list[str]:
    manifest = yaml.safe_load((ROOT / "docs" / "port_manifest.yaml").read_text(encoding="utf-8"))
    return [entry["port_name"] for entry in manifest["ports"]]


def _declared_protocol_names() -> set[str]:
    manifest_names = set(_manifest_port_names())
    names: set[str] = set()
    for name, value in inspect.getmembers(ports, inspect.isclass):
        if name in manifest_names and getattr(value, "_is_protocol", False):
            names.add(name)
    return names


def _method_names(protocol_name: str) -> set[str]:
    protocol = getattr(ports, protocol_name)
    return {
        name
        for name, value in inspect.getmembers(protocol)
        if inspect.isfunction(value) and not name.startswith("_")
    }


def test_all_manifest_ports_exist_as_protocols() -> None:
    manifest_names = set(_manifest_port_names())
    declared_names = _declared_protocol_names()
    assert declared_names == manifest_names
    assert len(declared_names) == 50
    assert all(getattr(getattr(ports, name), "_is_protocol", False) for name in manifest_names)


def test_expected_protocol_methods_exist() -> None:
    for protocol_name, expected_methods in EXPECTED_METHODS.items():
        assert _method_names(protocol_name) >= expected_methods


def test_admin_write_ports_do_not_merge_read_surface() -> None:
    for protocol_name in ADMIN_WRITE_PORTS:
        assert _method_names(protocol_name).isdisjoint(READ_METHODS)


def test_audit_key_provider_does_not_expose_raw_key_bytes() -> None:
    assert "current_key" not in _method_names("AuditKeyProvider")
