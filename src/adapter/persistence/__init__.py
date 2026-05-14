"""
module_id: adapter.persistence
file: src/adapter/persistence/__init__.py
task_id: T-310

Persistence adapters for project state, event logs, snapshots, audit reads, and authorisation reads.
"""

from __future__ import annotations

from adapter.persistence.filesystem_snapshot_store import FilesystemSnapshotStore
from adapter.persistence.jsonl_event_log import (
    EventLogDecodeError,
    EventStreamOwnershipError,
    JsonlEventLog,
)
from adapter.persistence.sqlite_audit_log import (
    AuditEntryNotFoundError,
    AuditLogTamperDetectedError,
    AuditLogTamperDetectionUnavailable,
    SqliteAuditLog,
    audit_row_message,
)
from adapter.persistence.sqlite_audit_log_writer import AuditLogWriterRow, SqliteAuditLogWriter
from adapter.persistence.sqlite_authorisation_store_read import (
    AuthorisationProfileNotFoundError,
    AuthorisationProfileTamperDetectedError,
    SqliteAuthorisationStoreRead,
    initialise_authorisation_schema,
    profile_from_json,
    profile_to_json,
)
from adapter.persistence.sqlite_authorisation_store_write import (
    AlreadyBootstrappedError,
    AuthorisationProfileAlreadyExistsError,
    SqliteAuthorisationStoreWrite,
)
from adapter.persistence.sqlite_project_store import ProjectNotFoundError, SqliteProjectStore
from adapter.persistence.sqlite_review_queue_store import (
    ReviewQueueItemNotFoundError,
    ReviewQueueRequestConflictError,
    SqliteReviewQueueStore,
)
from adapter.persistence.sqlite_sop_template_store import (
    SopTemplateAlreadyExistsError,
    SopTemplateBootstrapConfigurationError,
    SopTemplateNotFoundError,
    SqliteSopTemplateStore,
)

__all__ = [
    "AlreadyBootstrappedError",
    "AuditEntryNotFoundError",
    "AuditLogTamperDetectedError",
    "AuditLogTamperDetectionUnavailable",
    "AuditLogWriterRow",
    "AuthorisationProfileAlreadyExistsError",
    "AuthorisationProfileNotFoundError",
    "AuthorisationProfileTamperDetectedError",
    "EventLogDecodeError",
    "EventStreamOwnershipError",
    "FilesystemSnapshotStore",
    "JsonlEventLog",
    "ProjectNotFoundError",
    "ReviewQueueItemNotFoundError",
    "ReviewQueueRequestConflictError",
    "SopTemplateAlreadyExistsError",
    "SopTemplateBootstrapConfigurationError",
    "SopTemplateNotFoundError",
    "SqliteAuditLog",
    "SqliteAuditLogWriter",
    "SqliteAuthorisationStoreRead",
    "SqliteAuthorisationStoreWrite",
    "SqliteProjectStore",
    "SqliteReviewQueueStore",
    "SqliteSopTemplateStore",
    "audit_row_message",
    "initialise_authorisation_schema",
    "profile_from_json",
    "profile_to_json",
]
