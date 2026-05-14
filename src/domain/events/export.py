"""
module_id: domain.events.export
file: src/domain/events/export.py
task_id: T-305

Export-stream event subclasses.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.events.base import CanonicalPayload, ExportEvent, register_event_type


@register_event_type
@dataclass(frozen=True)
class ExportProfileRedactionApplied(ExportEvent):
    event_type = "ExportProfileRedactionApplied"
    export_profile_id: str
    redaction_policy_hash: str


@register_event_type
@dataclass(frozen=True)
class ExportBundleCreated(ExportEvent):
    event_type = "ExportBundleCreated"
    bundle_id: str
    bundle_hash: str
    artefact_manifest: CanonicalPayload
