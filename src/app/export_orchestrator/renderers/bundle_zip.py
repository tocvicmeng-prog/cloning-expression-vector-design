"""Deterministic ZIP renderer for final export bundles."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from io import BytesIO
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from domain.sequence import Sha256

from .manifest import ExportArtefact

MODULE_ID = "app.export_orchestrator.renderers.bundle_zip"
OWNING_TASKS = ("T-903",)


def render_bundle_zip(artefacts: tuple[ExportArtefact, ...], *, timestamp_utc: datetime) -> bytes:
    """Render a byte-stable ZIP by sorting paths and fixing entry metadata."""

    seen_paths: set[str] = set()
    buffer = BytesIO()
    with ZipFile(buffer, mode="w", compression=ZIP_STORED) as archive:
        for artefact in sorted(artefacts, key=lambda item: item.path):
            if artefact.path in seen_paths:
                raise ValueError(f"duplicate export artefact path: {artefact.path}")
            seen_paths.add(artefact.path)
            info = ZipInfo(filename=artefact.path, date_time=_zip_datetime(timestamp_utc))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, artefact.content)
    return buffer.getvalue()


def bundle_zip_hash(zip_bytes: bytes) -> Sha256:
    return Sha256(hashlib.sha256(zip_bytes).hexdigest())


def _zip_datetime(timestamp_utc: datetime) -> tuple[int, int, int, int, int, int]:
    if timestamp_utc.tzinfo is None:
        timestamp_utc = timestamp_utc.replace(tzinfo=UTC)
    normalised = timestamp_utc.astimezone(UTC).replace(microsecond=0)
    if normalised.year < 1980:
        normalised = normalised.replace(year=1980, month=1, day=1, hour=0, minute=0, second=0)
    return (
        normalised.year,
        normalised.month,
        normalised.day,
        normalised.hour,
        normalised.minute,
        normalised.second,
    )
