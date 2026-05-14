"""
module_id: app.plugin_governance
file: src/app/plugin_governance.py
task_id: T-808

Signed plugin-manifest verification and sandbox permission governance.
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Protocol, TypeAlias

import yaml  # type: ignore[import-untyped]
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from domain.canonicalisation import canonical_sha256
from domain.events import (
    DomainEvent,
    GovernanceEvent,
    PluginManifestApproved,
    PluginManifestRejected,
)
from domain.security import InstitutionId
from domain.sequence import Sha256

MODULE_ID = "app.plugin_governance"
OWNING_TASKS = ("T-808",)

DEFAULT_PLUGIN_TRUST_KEY_ID = "plugin-trust-seed-v1"
DEFAULT_PLUGIN_TRUST_PUBLIC_KEY_B64 = "A6EHv/POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg="

JsonObject: TypeAlias = dict[str, object]


class GovernanceEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class PluginGovernanceError(ValueError):
    """Raised when a plugin manifest cannot be parsed or trusted."""


@dataclass(frozen=True)
class PluginPermissions:
    file_access: tuple[str, ...] = ()
    network_access: bool = False
    deterministic_paths: bool = True
    network_hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_items(self.file_access, "file_access")
        _require_non_empty_items(self.network_hosts, "network_hosts")
        for path in self.file_access:
            _normalised_permission_path(path)
        if self.network_hosts and not self.network_access:
            raise PluginGovernanceError("network_hosts require network_access=true")

    def to_payload(self) -> dict[str, object]:
        return {
            "deterministic_paths": self.deterministic_paths,
            "file_access": sorted(self.file_access),
            "network_access": self.network_access,
            "network_hosts": sorted(self.network_hosts),
        }


@dataclass(frozen=True)
class PluginSignature:
    key_id: str
    algorithm: str
    signed_payload_hash: Sha256
    signature_b64: str

    def __post_init__(self) -> None:
        if not self.key_id:
            raise PluginGovernanceError("signature key_id cannot be empty")
        if self.algorithm != "ed25519":
            raise PluginGovernanceError("plugin manifests currently require ed25519")
        if not str(self.signed_payload_hash):
            raise PluginGovernanceError("signed_payload_hash cannot be empty")
        if not self.signature_b64:
            raise PluginGovernanceError("signature cannot be empty")

    @property
    def signature_bytes(self) -> bytes:
        try:
            return base64.b64decode(self.signature_b64.encode("ascii"), validate=True)
        except Exception as exc:
            raise PluginGovernanceError("signature must be base64") from exc


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    artefact_path: str
    artefact_sha256: Sha256
    permissions: PluginPermissions
    signature: PluginSignature | None
    citation: Mapping[str, object]
    manifest_path: Path

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.plugin_id, "plugin_id"),
            (self.name, "name"),
            (self.version, "version"),
            (self.artefact_path, "artefact_path"),
            (str(self.artefact_sha256), "artefact_sha256"),
        ):
            if not value:
                raise PluginGovernanceError(f"{field_name} cannot be empty")
        _normalised_permission_path(self.artefact_path)
        if not self.citation:
            raise PluginGovernanceError("citation cannot be empty")

    @property
    def artefact_absolute_path(self) -> Path:
        return (self.manifest_path.parent / self.artefact_path).resolve()

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "artefact_path": self.artefact_path,
            "artefact_sha256": str(self.artefact_sha256),
            "citation": dict(self.citation),
            "id": self.plugin_id,
            "name": self.name,
            "permissions": self.permissions.to_payload(),
            "version": self.version,
        }

    def manifest_hash(self) -> Sha256:
        return canonical_sha256(self.unsigned_payload())

    def signature_payload(self) -> bytes:
        return str(self.manifest_hash()).encode("ascii")


@dataclass(frozen=True)
class PluginTrustKey:
    key_id: str
    public_key_bytes: bytes
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.key_id:
            raise PluginGovernanceError("plugin trust key_id cannot be empty")
        if not self.public_key_bytes:
            raise PluginGovernanceError("plugin trust public key cannot be empty")

    @property
    def public_key(self) -> Ed25519PublicKey:
        return Ed25519PublicKey.from_public_bytes(self.public_key_bytes)


@dataclass(frozen=True)
class PluginTrustKeyring:
    keys: Mapping[str, PluginTrustKey]

    def __post_init__(self) -> None:
        if not self.keys:
            raise PluginGovernanceError("plugin trust keyring cannot be empty")

    def verify(self, manifest: PluginManifest) -> tuple[bool, str | None]:
        signature = manifest.signature
        if signature is None:
            return False, "signature_missing"
        key = self.keys.get(signature.key_id)
        if key is None:
            return False, "signature_key_unknown"
        if key.revoked:
            return False, "signature_key_revoked"
        if signature.signed_payload_hash != manifest.manifest_hash():
            return False, "signed_payload_hash_mismatch"
        try:
            key.public_key.verify(signature.signature_bytes, manifest.signature_payload())
        except InvalidSignature:
            return False, "signature_mismatch"
        return True, None


@dataclass(frozen=True)
class PluginSandboxPolicy:
    allowed_file_roots: tuple[str, ...]
    network_access_allowed: bool = False
    allowed_network_hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.allowed_file_roots:
            raise PluginGovernanceError("allowed_file_roots cannot be empty")
        _require_non_empty_items(self.allowed_file_roots, "allowed_file_roots")
        _require_non_empty_items(self.allowed_network_hosts, "allowed_network_hosts")
        for root in self.allowed_file_roots:
            _normalised_permission_path(root)
        if self.allowed_network_hosts and not self.network_access_allowed:
            raise PluginGovernanceError(
                "allowed_network_hosts require network_access_allowed=true"
            )

    def validate(self, permissions: PluginPermissions) -> tuple[str, ...]:
        failures: list[str] = []
        allowed_roots = tuple(_normalised_permission_path(root) for root in self.allowed_file_roots)
        for requested in permissions.file_access:
            normalised = _normalised_permission_path(requested)
            if not any(_path_is_within(normalised, root) for root in allowed_roots):
                failures.append(f"file_access_out_of_scope:{requested}")
        if permissions.deterministic_paths and permissions.network_access:
            failures.append("deterministic_plugin_network_access")
        if permissions.network_access and not self.network_access_allowed:
            failures.append("network_access_not_allowed")
        allowed_hosts = frozenset(self.allowed_network_hosts)
        for host in permissions.network_hosts:
            if host not in allowed_hosts:
                failures.append(f"network_host_out_of_scope:{host}")
        return tuple(sorted(failures))


@dataclass(frozen=True)
class PluginSandboxGrant:
    plugin_id: str
    file_access: tuple[str, ...]
    network_access: bool
    network_hosts: tuple[str, ...]
    deterministic_paths: bool

    def assert_file_access(self, path: str) -> None:
        normalised = _normalised_permission_path(path)
        if not any(
            _path_is_within(normalised, _normalised_permission_path(root))
            for root in self.file_access
        ):
            raise PermissionError(f"plugin {self.plugin_id} cannot access {path}")

    def assert_network_access(self, host: str) -> None:
        if not self.network_access:
            raise PermissionError(f"plugin {self.plugin_id} has no network access")
        if host not in self.network_hosts:
            raise PermissionError(f"plugin {self.plugin_id} cannot access network host {host}")


@dataclass(frozen=True)
class PluginGovernanceRequest:
    manifest_path: Path
    institution_id: InstitutionId
    occurred_at_utc: datetime
    event_id: str
    plugin_id: str | None = None
    actor_id: str = MODULE_ID

    def __post_init__(self) -> None:
        if not self.event_id:
            raise PluginGovernanceError("event_id cannot be empty")
        if not self.actor_id:
            raise PluginGovernanceError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise PluginGovernanceError("occurred_at_utc must be timezone-aware")


@dataclass(frozen=True)
class PluginGovernanceDecision:
    approved: bool
    plugin_id: str
    manifest_hash: Sha256 | None
    reason: str | None
    event: GovernanceEvent
    sandbox_grant: PluginSandboxGrant | None = None


@dataclass(frozen=True)
class PluginManifestDirectoryReport:
    decisions: tuple[PluginGovernanceDecision, ...]

    @property
    def passed(self) -> bool:
        return all(decision.approved for decision in self.decisions)

    @property
    def messages(self) -> tuple[str, ...]:
        return tuple(
            f"{decision.plugin_id}: {decision.reason}"
            for decision in self.decisions
            if not decision.approved and decision.reason is not None
        )


class PluginGovernanceService:
    def __init__(
        self,
        *,
        trust_keyring: PluginTrustKeyring | None = None,
        sandbox_policy: PluginSandboxPolicy | None = None,
        event_log: GovernanceEventLog | None = None,
    ) -> None:
        self._trust_keyring = trust_keyring or default_plugin_trust_keyring()
        self._sandbox_policy = sandbox_policy or default_plugin_sandbox_policy()
        self._event_log = event_log

    def review(self, request: PluginGovernanceRequest) -> PluginGovernanceDecision:
        try:
            manifest = _select_manifest(
                load_plugin_manifest_file(request.manifest_path),
                request.plugin_id,
            )
            return self._review_manifest(manifest, request)
        except PluginGovernanceError as exc:
            plugin_id = request.plugin_id or _best_effort_plugin_id(request.manifest_path)
            event = _rejected_event(request, plugin_id=plugin_id, reason=str(exc))
            self._append(event)
            return PluginGovernanceDecision(
                approved=False,
                plugin_id=plugin_id,
                manifest_hash=None,
                reason=str(exc),
                event=event,
            )

    def _review_manifest(
        self,
        manifest: PluginManifest,
        request: PluginGovernanceRequest,
    ) -> PluginGovernanceDecision:
        valid_signature, signature_reason = self._trust_keyring.verify(manifest)
        if not valid_signature:
            return self._reject(request, manifest, _expect_reason(signature_reason))
        artefact_reason = _artefact_hash_failure(manifest)
        if artefact_reason is not None:
            return self._reject(request, manifest, artefact_reason)
        permission_failures = self._sandbox_policy.validate(manifest.permissions)
        if permission_failures:
            return self._reject(
                request,
                manifest,
                "permission_denied:" + ",".join(permission_failures),
            )
        grant = PluginSandboxGrant(
            plugin_id=manifest.plugin_id,
            file_access=manifest.permissions.file_access,
            network_access=manifest.permissions.network_access,
            network_hosts=manifest.permissions.network_hosts,
            deterministic_paths=manifest.permissions.deterministic_paths,
        )
        event = PluginManifestApproved(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            institution_id=str(request.institution_id),
            plugin_id=manifest.plugin_id,
            manifest_hash=str(manifest.manifest_hash()),
        )
        self._append(event)
        return PluginGovernanceDecision(
            approved=True,
            plugin_id=manifest.plugin_id,
            manifest_hash=manifest.manifest_hash(),
            reason=None,
            event=event,
            sandbox_grant=grant,
        )

    def _reject(
        self,
        request: PluginGovernanceRequest,
        manifest: PluginManifest,
        reason: str,
    ) -> PluginGovernanceDecision:
        event = _rejected_event(request, plugin_id=manifest.plugin_id, reason=reason)
        self._append(event)
        return PluginGovernanceDecision(
            approved=False,
            plugin_id=manifest.plugin_id,
            manifest_hash=manifest.manifest_hash(),
            reason=reason,
            event=event,
        )

    def _append(self, event: GovernanceEvent) -> None:
        if self._event_log is not None:
            self._event_log.append_event(event.institution_id, event)


def load_plugin_manifest_file(path: str | Path) -> tuple[PluginManifest, ...]:
    manifest_path = Path(path)
    loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    root = _expect_mapping(loaded, "plugin manifest root")
    raw_manifests = _expect_array(root.get("manifests"), "manifests")
    manifests = tuple(
        _manifest_from_payload(_expect_mapping(raw, "manifest"), manifest_path)
        for raw in raw_manifests
    )
    if not manifests:
        raise PluginGovernanceError("manifest file must contain at least one manifest")
    return manifests


def evaluate_plugin_manifest_directory(
    manifest_root: str | Path,
    *,
    institution_id: str = "institution.default",
    occurred_at_utc: datetime,
    trust_keyring: PluginTrustKeyring | None = None,
    sandbox_policy: PluginSandboxPolicy | None = None,
) -> PluginManifestDirectoryReport:
    service = PluginGovernanceService(
        trust_keyring=trust_keyring,
        sandbox_policy=sandbox_policy,
    )
    root = Path(manifest_root)
    decisions: list[PluginGovernanceDecision] = []
    for path in sorted(root.glob("*.yaml")):
        for manifest in load_plugin_manifest_file(path):
            request = PluginGovernanceRequest(
                manifest_path=path,
                institution_id=InstitutionId(institution_id),
                occurred_at_utc=occurred_at_utc,
                event_id=f"plugin-manifest-signature:{manifest.plugin_id}",
                plugin_id=manifest.plugin_id,
            )
            decisions.append(service.review(request))
    return PluginManifestDirectoryReport(decisions=tuple(decisions))


def default_plugin_trust_keyring() -> PluginTrustKeyring:
    return PluginTrustKeyring(
        keys={
            DEFAULT_PLUGIN_TRUST_KEY_ID: PluginTrustKey(
                key_id=DEFAULT_PLUGIN_TRUST_KEY_ID,
                public_key_bytes=base64.b64decode(DEFAULT_PLUGIN_TRUST_PUBLIC_KEY_B64),
            )
        }
    )


def default_plugin_sandbox_policy() -> PluginSandboxPolicy:
    return PluginSandboxPolicy(
        allowed_file_roots=("plugins", "catalogues/plugin_manifests/artifacts"),
        network_access_allowed=False,
    )


def plugin_manifest_signature_payload(unsigned_manifest_payload: Mapping[str, object]) -> bytes:
    return str(canonical_sha256(unsigned_manifest_payload)).encode("ascii")


def _manifest_from_payload(raw: Mapping[str, object], manifest_path: Path) -> PluginManifest:
    return PluginManifest(
        plugin_id=_expect_str(raw, "id"),
        name=_expect_str(raw, "name"),
        version=_expect_str(raw, "version"),
        artefact_path=_expect_str(raw, "artefact_path"),
        artefact_sha256=Sha256(_expect_str(raw, "artefact_sha256")),
        permissions=_permissions_from_payload(raw.get("permissions")),
        signature=_signature_from_payload(raw.get("signature")),
        citation=_expect_mapping(raw.get("citation"), "citation"),
        manifest_path=manifest_path,
    )


def _permissions_from_payload(raw: object) -> PluginPermissions:
    data = _expect_mapping(raw, "permissions")
    network_access = data.get("network_access", False)
    deterministic_paths = data.get("deterministic_paths", True)
    if not isinstance(network_access, bool):
        raise PluginGovernanceError("permissions.network_access must be boolean")
    if not isinstance(deterministic_paths, bool):
        raise PluginGovernanceError("permissions.deterministic_paths must be boolean")
    return PluginPermissions(
        file_access=_expect_str_tuple(data.get("file_access", []), "permissions.file_access"),
        network_access=network_access,
        deterministic_paths=deterministic_paths,
        network_hosts=_expect_str_tuple(data.get("network_hosts", []), "permissions.network_hosts"),
    )


def _signature_from_payload(raw: object) -> PluginSignature | None:
    if raw is None:
        return None
    data = _expect_mapping(raw, "signature")
    return PluginSignature(
        key_id=_expect_str(data, "key_id"),
        algorithm=_expect_str(data, "algorithm"),
        signed_payload_hash=Sha256(_expect_str(data, "signed_payload_hash")),
        signature_b64=_expect_str(data, "signature"),
    )


def _artefact_hash_failure(manifest: PluginManifest) -> str | None:
    path = manifest.artefact_absolute_path
    if not path.is_file():
        return "artefact_missing"
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != str(manifest.artefact_sha256):
        return "artefact_hash_mismatch"
    return None


def _select_manifest(
    manifests: tuple[PluginManifest, ...],
    plugin_id: str | None,
) -> PluginManifest:
    if plugin_id is None:
        if len(manifests) != 1:
            raise PluginGovernanceError("plugin_id is required for multi-manifest files")
        return manifests[0]
    for manifest in manifests:
        if manifest.plugin_id == plugin_id:
            return manifest
    raise PluginGovernanceError(f"manifest not found for plugin_id: {plugin_id}")


def _rejected_event(
    request: PluginGovernanceRequest,
    *,
    plugin_id: str,
    reason: str,
) -> PluginManifestRejected:
    return PluginManifestRejected(
        event_id=request.event_id,
        occurred_at_utc=request.occurred_at_utc,
        actor_id=request.actor_id,
        institution_id=str(request.institution_id),
        plugin_id=plugin_id,
        reason=reason,
    )


def _best_effort_plugin_id(path: Path) -> str:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        root = _expect_mapping(loaded, "plugin manifest root")
        manifests = _expect_array(root.get("manifests"), "manifests")
        first = _expect_mapping(manifests[0], "manifest") if manifests else {}
        raw_id = first.get("id")
        if isinstance(raw_id, str) and raw_id:
            return raw_id
    except Exception:
        pass
    return path.stem


def _expect_reason(reason: str | None) -> str:
    if reason is None:
        raise PluginGovernanceError("missing rejection reason")
    return reason


def _expect_mapping(raw: object, name: str) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        raise PluginGovernanceError(f"{name} must be a mapping")
    return {str(key): value for key, value in raw.items()}


def _expect_array(raw: object, name: str) -> tuple[object, ...]:
    if not isinstance(raw, list):
        raise PluginGovernanceError(f"{name} must be an array")
    return tuple(raw)


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise PluginGovernanceError(f"{key} must be a non-empty string")
    return value


def _expect_str_tuple(raw: object, name: str) -> tuple[str, ...]:
    values = _expect_array(raw, name)
    strings = tuple(value for value in values if isinstance(value, str) and value)
    if len(strings) != len(values):
        raise PluginGovernanceError(f"{name} must contain only non-empty strings")
    return strings


def _normalised_permission_path(value: str) -> str:
    normalised = PurePosixPath(value.replace("\\", "/")).as_posix().strip("/")
    if not normalised or normalised == ".":
        raise PluginGovernanceError("permission paths cannot be empty")
    if any(part in {"", ".", ".."} for part in normalised.split("/")):
        raise PluginGovernanceError(f"permission path is not sandbox-safe: {value}")
    return normalised


def _path_is_within(path: str, root: str) -> bool:
    return path == root or path.startswith(f"{root}/")


def _require_non_empty_items(values: Iterable[str], field_name: str) -> None:
    if any(not value for value in values):
        raise PluginGovernanceError(f"{field_name} cannot contain empty values")


__all__ = [
    "DEFAULT_PLUGIN_TRUST_KEY_ID",
    "PluginGovernanceDecision",
    "PluginGovernanceError",
    "PluginGovernanceRequest",
    "PluginGovernanceService",
    "PluginManifest",
    "PluginManifestDirectoryReport",
    "PluginPermissions",
    "PluginSandboxGrant",
    "PluginSandboxPolicy",
    "PluginSignature",
    "PluginTrustKey",
    "PluginTrustKeyring",
    "default_plugin_sandbox_policy",
    "default_plugin_trust_keyring",
    "evaluate_plugin_manifest_directory",
    "load_plugin_manifest_file",
    "plugin_manifest_signature_payload",
]
