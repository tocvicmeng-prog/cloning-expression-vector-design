# T-316a Post-Execution Note

## Files Written

- `src/domain/ports/sop_template.py` read/admin/bootstrap/sign/verifier Protocols.
- `src/domain/types/sop_template.py` `SopTemplate`, `SopTemplateSignature`,
  `SopTemplateVersion`, and `SopTemplateRevocation`.
- `src/domain/types/signing_errors.py` extended with SOP-template verification errors.
- `src/domain/ports/__init__.py` and `src/domain/types/__init__.py` exports updated.
- `tests/fakes/sop_template/` deterministic SOP-template signer/verifier fake and fixtures.
- `tests/domain/types/test_sop_template.py` and `tests/domain/ports/test_sop_template_contract.py`.
- `tasks/task_brief/T-316a.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.11 (`T-316a`).
- `ARCHITECTURE.md` B3-05 / B4-05 / H4-04 signed SOP-template split.
- `ROADMAP.md` Phase 3 prerequisite for T-316b and T-803 consuming `SopTemplateReadPort`.

## Verification

- `python -m uv run --no-editable pytest tests\domain\types\test_sop_template.py tests\domain\ports\test_sop_template_contract.py tests\fakes\sop_template\test_fake_signer.py tests\ports\test_port_inventory.py --cov=domain.ports --cov=domain.types.sop_template --cov=domain.types.signing_errors --cov-report=term-missing --cov-fail-under=85`:
  9 passed, 93.59% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  187 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-308 is next in Phase 3. T-316b remains in Phase 4 and owns the signed SQLite SOP-template store
and bootstrap migration after catalogue schema/content exist; T-803 should consume only
`SopTemplateReadPort`.
