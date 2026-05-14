# T-313a Post-Execution Note

## Files Written

- `src/domain/ports/audit_append.py` append-only `AuditAppendPort`,
  `AdminAuditAppendPort`, `AuditEntry`, and `AuditEntryId`.
- `src/domain/security/service_principals.py` engine-internal `ServicePrincipal` and
  `ServiceName` values.
- `src/domain/ports/__init__.py` and `src/domain/security/__init__.py` exports updated.
- `tests/fakes/security/audit_append/` deterministic fake engine/admin brokers sharing a single
  in-memory HMAC chain.
- `tests/domain/ports/test_audit_append_contract.py` reusable append-port contract test.
- `tests/security/test_audit_append_chain_integrity_helpers.py` helper tests for tamper and broken
  link detection.
- `tests/fakes/security/audit_key/provider.py` fixed `verify_with_archived()` so current-key rows
  also verify the MAC instead of accepting any current-key message.
- `tasks/task_brief/T-313a.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.9 (`T-313a`).
- `ARCHITECTURE.md` B3-01 / B4-03 / B4-04 audit-append split and single-writer audit-service
  boundary.
- `ROADMAP.md` Phase 3 prerequisite for T-310/T-311 audit-chain and admin-service work.

## Verification

- `python -m uv run --no-editable pytest tests\fakes\security\audit_key\test_audit_key_provider.py tests\domain\ports\test_audit_key_provider_contract.py tests\security\test_audit_append_chain_integrity_helpers.py tests\fakes\security\audit_append\test_fake_brokers.py tests\domain\ports\test_audit_append_contract.py tests\ports\test_port_inventory.py --cov=domain.ports --cov=domain.security.service_principals --cov-report=term-missing --cov-fail-under=85`:
  17 passed, 96.97% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  176 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-314a can now add profile/decision signing Protocols against an audit append surface that already
separates engine service callers from admin-service callers. T-310/T-311 should use the fake brokers
and `assert_linear_hmac_chain()` helper for HMAC-chain integration tests until T-313b provides the
production audit-service IPC writer.
