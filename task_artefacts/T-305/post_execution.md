# T-305 Post-Execution Note

## Files Written

- `src/domain/events/` package replacing the T-203 `domain.events` stub:
  base event serialization, design stream, governance stream, export stream, and package exports.
- `tests/domain/events/test_events.py` covering round-trip serialization, stream ownership, active
  advisory presentation fields, and self-contained governance payloads.
- `.gitignore` runtime artefact entries narrowed from `events/` to `/events/` so
  `src/domain/events` is included in non-editable Hatch builds.
- `tasks/task_brief/T-305.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.5 (`T-305`).
- `ARCHITECTURE.md` § 4.7 and event-stream split in § 4.8.
- Fixes B2-05, H3-06, B3-03, and v1.5 FR-ADV active-advisory event requirements at the
  domain-event schema level.

## Verification

- `python -m uv run --no-editable pytest tests\domain\events --cov=domain.events --cov-fail-under=85`:
  10 passed, 97.98% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  112 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 2 contracts kept.

## Downstream Notes

T-306 still owns the concrete risk-advisory/governance value-object namespaces. T-305 event
classes carry canonical payload tuples plus hashes so the stream is already self-contained without
pre-implementing those later value objects.
