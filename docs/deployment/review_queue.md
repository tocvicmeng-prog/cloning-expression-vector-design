# Review Queue Deployment Notes

`app.review_queue` owns the Phase-3 recovery path for blocked operational-protocol authorisation and user extension requests.

## Runtime Shape

- User and engine/service callers submit requests through `ReviewQueueService`.
- `ReviewQueueService` receives only `ReviewQueueStore`, `AuditAppendPort`, a governance-event log, and the review-queue `ServicePrincipal`.
- Admin resolution is intentionally absent from the user-facing service. Resolution goes through `ReviewQueueAdminPort`, composed by the future admin-service IPC implementation.
- `SqliteReviewQueueStore` persists immutable request rows in `review_queue_requests` and appends admin decisions to `review_queue_decisions`.
- Item status is derived from the latest decision row. Request rows are never updated.

## Operational Invariants

- Repeated blocked-authorisation routing for the same session, user, scope, and reason returns the existing item and does not duplicate queue entries.
- Submitting a user extension request never mutates `authorisation.sqlite`.
- Queue approval alone never grants access. The admin must still mint or modify an `AuthorisationProfile` through `app.admin_action_handler`.
- `UserPrincipal` and `ReviewerPrincipal` attempts to resolve queue items raise `PermissionError` and emit `AuthorisationAttemptDenied`.

## Files

- Queue DB: `review_queue.sqlite`
- Request/event audit path: `AuditAppendPort` via the audit-service IPC client in production
- Governance stream: `events/governance/<institution>.jsonl`

## Verification

```powershell
python -m uv run --no-editable pytest tests\app\review_queue tests\ports\test_port_inventory.py tests\domain\events\test_events.py --cov=app.review_queue --cov=app.review_queue_service --cov=adapter.persistence.sqlite_review_queue_store --cov=domain.types.review_queue --cov=domain.ports.review_queue_admin --cov-report=term-missing --cov-fail-under=85
```
