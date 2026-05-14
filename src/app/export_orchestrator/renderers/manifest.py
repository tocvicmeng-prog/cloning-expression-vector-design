"""Canonical export-bundle manifest renderer."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from domain.canonicalisation import canonical_json
from domain.sequence import Sha256

MODULE_ID = "app.export_orchestrator.renderers.manifest"
OWNING_TASKS = ("T-903",)


@dataclass(frozen=True, slots=True)
class ExportArtefact:
    path: str
    media_type: str
    content: bytes

    def __post_init__(self) -> None:
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts or "\\" in self.path:
            raise ValueError(f"unsafe export artefact path: {self.path!r}")
        if not self.path or self.path.endswith("/"):
            raise ValueError("export artefact path must name a file")
        if not self.media_type:
            raise ValueError("export artefact media type is required")

    @property
    def content_hash(self) -> Sha256:
        return Sha256(hashlib.sha256(self.content).hexdigest())


def render_manifest(
    *,
    bundle_id: str,
    export_profile_id: str,
    derivation_environment_hash: Sha256,
    artefacts: tuple[ExportArtefact, ...],
    metadata: dict[str, Any],
) -> str:
    payload = build_manifest_payload(
        bundle_id=bundle_id,
        export_profile_id=export_profile_id,
        derivation_environment_hash=derivation_environment_hash,
        artefacts=artefacts,
        metadata=metadata,
    )
    return canonical_json(payload).decode("utf-8")


def build_manifest_payload(
    *,
    bundle_id: str,
    export_profile_id: str,
    derivation_environment_hash: Sha256,
    artefacts: tuple[ExportArtefact, ...],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    seen_paths: set[str] = set()
    manifest_artefacts: list[dict[str, Any]] = []
    for artefact in sorted(artefacts, key=lambda item: item.path):
        if artefact.path in seen_paths:
            raise ValueError(f"duplicate export artefact path: {artefact.path}")
        seen_paths.add(artefact.path)
        manifest_artefacts.append(
            {
                "path": artefact.path,
                "media_type": artefact.media_type,
                "size_bytes": len(artefact.content),
                "sha256": str(artefact.content_hash),
            }
        )
    return {
        "schema": "cloning-expression-vector.export-manifest.v1",
        "bundle_id": bundle_id,
        "export_profile_id": export_profile_id,
        "derivation_environment_hash": str(derivation_environment_hash),
        "artefact_count": len(manifest_artefacts),
        "artefacts": manifest_artefacts,
        "metadata": metadata,
    }


def manifest_event_payload(
    *,
    bundle_id: str,
    manifest_json: str,
    artefacts: tuple[ExportArtefact, ...],
) -> tuple[tuple[str, str], ...]:
    artefact_names = ",".join(
        artefact.path for artefact in sorted(artefacts, key=lambda item: item.path)
    )
    return (
        ("bundle_id", bundle_id),
        ("manifest_sha256", str(Sha256(hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()))),
        ("artefact_count", str(len(artefacts))),
        ("artefact_names", artefact_names),
    )
