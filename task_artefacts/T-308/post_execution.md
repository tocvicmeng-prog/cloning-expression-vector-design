# T-308 Post-Execution Note

## Files Written

- `src/adapter/io/` package with GenBank, FASTA, SBOL3, SnapGene `.dna`, imported construct, and write-result adapters/contracts.
- `tests/adapter/io/test_sequence_io.py` adapter round-trip and invariant coverage.
- `tasks/task_brief/T-308.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.12 (`T-308`).
- `ARCHITECTURE.md` sequence I/O contract for `ImportedConstruct` / `AnnotatedConstruct`.
- `ROADMAP.md` Phase 3 sequence I/O hand-off; T-902 depends on `SnapGeneDnaReader`.

## Verification

- `python -m uv run --no-editable pytest tests\adapter\io\test_sequence_io.py --cov=adapter.io --cov-report=term-missing --cov-fail-under=85`:
  5 passed, 87.61% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  192 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-309 is next in Phase 3. The SBOL3 adapter currently preserves sequence deterministically and reports
feature loss when feature annotations are present; GenBank remains the feature-preserving interchange path.
SnapGene `.dna` parsing is read-only and raises an actionable error for corrupted or unsupported proprietary
files, instructing users to export GenBank from SnapGene.
