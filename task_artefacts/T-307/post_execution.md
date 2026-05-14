# T-307 Post-Execution Note

## Files Written

- `src/domain/canonicalisation/` RFC 8785/JCS canonical JSON package with project `$$cev:`
  tagged scalar support.
- `src/domain/types/derivation/` derivation environment, policy enums, typed identifiers,
  optimisation settings, user overrides, and reviewer decisions.
- `src/domain/types/__init__.py` exports the non-operational derivation value objects.
- `tests/fixtures/canonicalisation/golden/vectors.json` with 32 canonical JSON golden vectors.
- `tests/canonicalisation/test_jcs_golden_vectors.py` canonical JSON, hash, and rejection tests.
- `tests/domain/types/test_derivation_environment.py` derivation-environment determinism tests.
- `tasks/task_brief/T-307.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.7 (`T-307`).
- `ARCHITECTURE.md` C6, B11, M2, M3-07, and R-02 determinism/provenance requirements.
- `ROADMAP.md` Phase 3 derivation-environment completeness and replay-determinism prerequisites.

## Verification

- `python -m uv run --no-editable pytest tests\canonicalisation tests\domain\types\test_derivation_environment.py --cov=domain.canonicalisation --cov=domain.types.derivation --cov-report=term-missing --cov-fail-under=85`:
  43 passed, 92.46% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  163 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-312a can now define the `AuditKeyProvider` Protocol against a deterministic canonical hashing
foundation. Later replay and export tasks should use `domain.canonicalisation.canonical_json` rather
than ad hoc `json.dumps(sort_keys=True)`.
