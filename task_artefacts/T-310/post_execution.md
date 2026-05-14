# T-310 Post-Execution Note

## Files Written

- `src/adapter/persistence/` package with SQLite project store, JSONL event log, SQLite audit reader, read-only authorisation store, and filesystem snapshot store.
- `src/adapter/persistence/schemas/` SQL seed schemas for project, audit, and authorisation stores.
- `tests/adapter/persistence/` persistence adapter tests.
- `tasks/task_brief/T-310.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.14 (`T-310`).
- `ARCHITECTURE.md` § 4.5 ProjectStore/EventLog/AuditLog/AuthorisationStore ports.
- `CODING_AGENDA.md` § 3.4 persistence table and read-only authorisation enforcement.

## Verification

- `python -m uv run --no-editable pytest tests\adapter\persistence tests\engine\session --cov=adapter.persistence --cov=engine.session --cov-report=term-missing --cov-fail-under=85`:
  31 passed, 87.89% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  223 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-311 is next and owns the admin write path for authorisation profiles. T-310 ships only the read-side
authorisation adapter and the audit-log read/verification surface; production audit appends remain routed
through the T-313a/T-313b append-port/audit-service boundary.
