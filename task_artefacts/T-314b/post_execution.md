# T-314b Post-Execution Note

## Files Written

- `src/adapter/security/signing_key_archive.py` shared Ed25519 key archive.
- `src/adapter/security/profile_signing/` institutional profile signer/verifier.
- `src/adapter/security/decision_record_signing/` per-principal decision-record signer/verifier.
- `src/app/decision_record_key_management.py` provisioning, rotation, revocation, and governance events.
- `tools/profile_signature_verifier.py` and `tools/decision_record_verifier.py` offline verifiers.
- `docs/security/profile_signing_runbook.md` and `docs/security/decision_record_signing_runbook.md`.
- `tests/security/profile_signing/` and `tests/security/decision_record_signing/`.
- `tasks/task_brief/T-314b.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.17 (`T-314b`).
- `CODING_AGENDA.md` B3-04 profile signatures and B4-09 production `DecisionRecordSigner` ownership.
- `CODING_AGENDA.md` v1.4 cryptographic identity separation rule.

## Verification

- `python -m uv run --no-editable pytest tests\security\profile_signing tests\security\decision_record_signing tests\domain\ports\test_profile_signing_contract.py tests\domain\ports\test_decision_record_signing_contract.py tests\fakes\security\profile_signing --cov=adapter.security.profile_signing --cov=adapter.security.decision_record_signing --cov=adapter.security.signing_key_archive --cov=app.decision_record_key_management --cov=tools.profile_signature_verifier --cov=tools.decision_record_verifier --cov-report=term-missing --cov-fail-under=85`:
  21 passed, 89.85% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  265 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-313b is next and can authenticate audit-service IPC calls with the production `DecisionRecordVerifier`.
