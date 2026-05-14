# T-304 Post-Execution Note

## Files Written

- `src/domain/security/` package replacing the T-203 `domain.security` stub:
  identifiers, roles, operational roles, principals, profile signatures, dual-control flags,
  unsigned drafts, signed authorisation profiles, user declarations, and decisions.
- `tests/domain/security/` tests for role inheritance, bootstrap authority, profile signing
  invariants, scope validation, decisions, declarations, and dual-control defaults.
- `tasks/task_brief/T-304.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.4 (`T-304`).
- `ARCHITECTURE.md` § 4.6 roles/principals/authorisation model.
- Audit fixes M6, B4, B9, B3-04, and H3-10.

## Verification

- `python -m uv run --no-editable pytest tests\domain\security --cov=domain.security --cov-fail-under=85`:
  10 passed, 95.56% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  102 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 2 contracts kept.

## Downstream Notes

T-314a/T-314b still own signer/verifier Protocols and production cryptographic adapters. T-304
only enforces content-hash and profile-signature consistency at the domain boundary.
