# T-312a Post-Execution Note

## Files Written

- `src/domain/ports/audit_key.py` typed `AuditKeyProvider` Protocol with `KeyVersionId`
  and `MacBytes`.
- `src/domain/ports/__init__.py` re-exported the concrete audit-key Protocol while keeping the
  50-port inventory stable.
- `tests/fakes/security/audit_key/` deterministic `TestAuditKeyProvider` and rotation log value.
- `tests/domain/ports/test_audit_key_provider_contract.py` reusable provider contract test.
- `tests/ports/test_port_inventory.py` adjusted to accept Protocols re-exported from port modules.
- `tasks/task_brief/T-312a.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.8 (`T-312a`).
- `ARCHITECTURE.md` B3-02 / H4-10 audit-key split and raw-key exposure removal.
- `ROADMAP.md` Phase 3 audit-key prerequisite for T-310/T-311 audit HMAC-chain work.

## Verification

- `python -m uv run --no-editable pytest tests\domain\ports\test_audit_key_provider_contract.py tests\fakes\security\audit_key\test_audit_key_provider.py tests\ports\test_port_inventory.py --cov=domain.ports --cov-report=term-missing --cov-fail-under=85`:
  10 passed, 100% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  169 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-313a can now compute fake audit-chain rows through `AuditKeyProvider.mac()` without receiving
raw key bytes. T-310/T-311 should depend on the Protocol and the contract test helper, not on the
fake provider's private key storage.
