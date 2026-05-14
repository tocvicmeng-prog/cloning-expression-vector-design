# T-312b Post-Execution Note

## Files Written

- `src/adapter/security/audit_key/` production audit-key provider package with file escrow backend, backend selector, and OS-keystore fallback facades.
- `src/app/audit_key_rotation_service.py` admin/bootstrap rotation workflow.
- `tools/audit_key_verifier.py` standalone offline verifier for `audit.sqlite`.
- `docs/security/audit_key_runbook.md` provisioning, rotation, recovery, compromise, and offline-verification procedure.
- `tests/security/audit_key/` acceptance and adversarial tests.
- `tasks/task_brief/T-312b.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.16 (`T-312b`).
- `CODING_AGENDA.md` B2-08 / B3-02 audit-key lifecycle split.
- `CODING_AGENDA.md` B3-03 governance events embed signed payloads.
- `CODING_AGENDA.md` H4-05 indefinite audit-key archive retention and H4-10 no raw key exposure.

## Verification

- `python -m uv run --no-editable pytest tests\security\audit_key tests\domain\ports\test_audit_key_provider_contract.py tests\fakes\security\audit_key --cov=adapter.security.audit_key --cov=app.audit_key_rotation_service --cov=tools.audit_key_verifier --cov-report=term-missing --cov-fail-under=85`:
  27 passed, 90.36% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  250 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-314b is next. It must implement production institutional profile-signing and per-principal `DecisionRecordSigner` key lifecycle while keeping those signature keys separate from the T-312b institutional audit HMAC key.
