"""
module_id: domain.ports
file: src/domain/ports/__init__.py
task_id: T-203

Canonical Protocol inventory for architecture boundary ports.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from domain.ports.admin_service import AdminServiceClientPort
from domain.ports.audit_append import AdminAuditAppendPort, AuditAppendPort
from domain.ports.audit_key import AuditKeyProvider
from domain.ports.authorisation import (
    AuthorisationAdminWritePort,
    AuthorisationBootstrapPort,
    AuthorisationReadPort,
)
from domain.ports.decision_record_signing import DecisionRecordSigner, DecisionRecordVerifier
from domain.ports.profile_signing import AuthorisationProfileSigner, AuthorisationProfileVerifier
from domain.ports.review_queue_admin import ReviewQueueAdminPort, ReviewQueueStore
from domain.ports.sop_template import (
    SopTemplateAdminWritePort,
    SopTemplateBootstrapPort,
    SopTemplateReadPort,
    SopTemplateSigner,
    SopTemplateVerifier,
)

Payload = Mapping[str, object]
PayloadSequence = Sequence[Payload]

__all__ = [
    "AdminAuditAppendPort",
    "AdminServiceClientPort",
    "AdvisoryTextPolicy",
    "AuditAppendPort",
    "AuditKeyProvider",
    "AuditLog",
    "AuditLogReadPort",
    "AuthorisationAdminWritePort",
    "AuthorisationBootstrapPort",
    "AuthorisationProfileSigner",
    "AuthorisationProfileVerifier",
    "AuthorisationReadPort",
    "CodonAlgorithm",
    "DecisionRecordSigner",
    "DecisionRecordVerifier",
    "EnzymeCatalogue",
    "EventLog",
    "ExportProfileCatalogue",
    "HostCatalogue",
    "InstitutionalPolicy",
    "KozakScorer",
    "LLMConstraintTranslator",
    "Lifecycle",
    "MarkersCataloguePort",
    "PartCatalogue",
    "PluginManifestRegistry",
    "ProjectStore",
    "RefreshableAdapter",
    "ReviewQueueAdminPort",
    "ReviewQueueStore",
    "RiskAdvisoryCatalogue",
    "RnaFolder",
    "RuleRegistry",
    "ScreeningAdapter",
    "ScreeningProviderTrustPolicy",
    "SequenceReader",
    "SequenceWriter",
    "SignalPeptidePredictor",
    "SnapGeneChannel",
    "SnapGeneDnaReader",
    "SnapshotStore",
    "SopTemplateAdminWritePort",
    "SopTemplateBootstrapPort",
    "SopTemplateReadPort",
    "SopTemplateSigner",
    "SopTemplateVerifier",
    "SplicePredictor",
    "SynthesisVendorAdapter",
    "TIRPredictor",
    "ThresholdProfileCatalogue",
    "WorkerPoolFactory",
]


class PartCatalogue(Protocol):
    def get_part(self, part_id: str) -> Payload: ...
    def list_parts(self) -> PayloadSequence: ...


class HostCatalogue(Protocol):
    def get_host(self, host_id: str) -> Payload: ...
    def list_hosts(self) -> PayloadSequence: ...


class EnzymeCatalogue(Protocol):
    def get_enzyme(self, enzyme_id: str) -> Payload: ...
    def list_enzymes(self) -> PayloadSequence: ...


class MarkersCataloguePort(Protocol):
    """Read-only port over the selection-markers catalogue.

    Added by v0.2 Enrichment Amendment (2026-05-23, task T-409) as canonical
    port #51 per ARCHITECTURE.md § 9.2. Replaces the deprecated
    `parts.yaml::markers` block during the dual-read migration window.
    Backing data: `catalogues/markers.yaml` validated by
    `schemas/markers.schema.json` v1.0.
    """

    def get_marker(self, marker_id: str) -> Payload: ...
    def list_markers(self) -> PayloadSequence: ...
    def list_compatible_with_host_class(self, host_class: str) -> PayloadSequence: ...


class RuleRegistry(Protocol):
    def get_rule(self, rule_id: str) -> Payload: ...
    def list_rules(self) -> PayloadSequence: ...


class RiskAdvisoryCatalogue(Protocol):
    def get_advisory(self, advisory_id: str) -> Payload: ...
    def list_advisories(self) -> PayloadSequence: ...


class ScreeningProviderTrustPolicy(Protocol):
    def get_provider_policy(self, provider_id: str) -> Payload: ...
    def list_provider_policies(self) -> PayloadSequence: ...


class InstitutionalPolicy(Protocol):
    def get_policy(self, policy_id: str) -> Payload: ...
    def active_policy(self) -> Payload: ...


class ExportProfileCatalogue(Protocol):
    def get_export_profile(self, profile_id: str) -> Payload: ...
    def list_export_profiles(self) -> PayloadSequence: ...


class PluginManifestRegistry(Protocol):
    def get_manifest(self, plugin_id: str) -> Payload: ...
    def list_manifests(self) -> PayloadSequence: ...


class ThresholdProfileCatalogue(Protocol):
    def get_threshold_profile(self, profile_id: str) -> Payload: ...
    def list_threshold_profiles(self) -> PayloadSequence: ...


class ProjectStore(Protocol):
    def save_project(self, project: Payload) -> str: ...
    def load_project(self, project_id: str) -> Payload: ...


class EventLog(Protocol):
    def append(self, stream_id: str, event: Payload) -> str: ...
    def read_stream(self, stream_id: str) -> PayloadSequence: ...


class AuditLog(Protocol):
    def read_entry(self, entry_id: str) -> Payload: ...
    def verify_chain(self) -> bool: ...


class SnapshotStore(Protocol):
    def write_snapshot(self, session_id: str, event_seq: int, snapshot: Payload) -> str: ...
    def read_latest_snapshot(self, session_id: str) -> Payload | None: ...


class AuditLogReadPort(Protocol):
    def read_entry(self, entry_id: str) -> Payload: ...
    def replay(self) -> PayloadSequence: ...
    def verify_chain(self) -> bool: ...


class SequenceReader(Protocol):
    def read(self, source: bytes, *, format_name: str) -> Payload: ...


class SequenceWriter(Protocol):
    def write(self, construct: Payload, *, format_name: str) -> bytes: ...


class SnapGeneChannel(Protocol):
    def watch(self, path: str) -> Iterable[Payload]: ...


class SnapGeneDnaReader(Protocol):
    def read_dna(self, source: bytes) -> Payload: ...


class RnaFolder(Protocol):
    def fold(self, sequence: str) -> Payload: ...


class SplicePredictor(Protocol):
    def predict_splice_effects(self, sequence: str) -> PayloadSequence: ...


class SignalPeptidePredictor(Protocol):
    def predict_signal_peptide(self, protein_sequence: str) -> Payload: ...


class TIRPredictor(Protocol):
    def predict_tir(self, sequence: str, host_context: Payload) -> Payload: ...


class KozakScorer(Protocol):
    def score_kozak(self, sequence: str, host_context: Payload) -> Payload: ...


class CodonAlgorithm(Protocol):
    def optimise(self, coding_sequence_design: Payload) -> Payload: ...


class WorkerPoolFactory(Protocol):
    def create_pool(self, profile: Payload) -> Payload: ...


class SynthesisVendorAdapter(Protocol):
    def check(self, request: Payload) -> Payload: ...
    def quote(self, request: Payload) -> Payload: ...


class ScreeningAdapter(Protocol):
    def screen(self, request: Payload) -> Payload: ...


class LLMConstraintTranslator(Protocol):
    def translate(self, free_text: str, policy: Payload) -> Payload: ...


class AdvisoryTextPolicy(Protocol):
    def validate(self, advisory_text: str) -> Payload: ...


class Lifecycle(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...


class RefreshableAdapter(Protocol):
    def refresh(self) -> None: ...
