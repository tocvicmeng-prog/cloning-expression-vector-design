# T-311 Post-Execution Note

## Files Written

- `src/domain/ports/authorisation.py` split read/admin/bootstrap Protocols.
- `src/adapter/persistence/sqlite_authorisation_store_write.py` admin-service write adapter.
- `src/app/admin_action_handler.py` mint/modify/revoke/list/audit/bootstrap application service.
- `tests/app/admin_action_handler/` admin write, denial, and bootstrap tests.
- `tasks/task_brief/T-311.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.15 (`T-311`).
- `ARCHITECTURE.md` v1.5 authorisation profile admin-only write boundary.
- `CODING_AGENDA.md` B3-01 audit append broker and B3-04 profile-signature-on-write/read requirements.

## Verification

- `python -m uv run --no-editable pytest tests\app\admin_action_handler tests\adapter\persistence\test_sqlite_authorisation_store_read.py tests\fakes\security\profile_signing\test_fake_signers.py --cov=app.admin_action_handler --cov=adapter.persistence.sqlite_authorisation_store_write --cov=adapter.persistence.sqlite_authorisation_store_read --cov=domain.ports.authorisation --cov-report=term-missing --cov-fail-under=85`:
  13 passed, 92.64% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  229 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-312b is next and owns production audit-key keystore adapters, rotation, and offline verification. T-311 uses
the deterministic T-314a profile signer/verifier and T-313a fake admin audit append path in tests; production
cryptographic adapters remain scheduled for T-314b/T-313b.
