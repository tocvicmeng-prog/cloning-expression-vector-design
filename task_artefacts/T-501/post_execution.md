# T-501 Post-Execution Handover

## Status

verified locally

## Files written

- `src/engine/dependencies.py` — deterministic validation dependency graph, impact computation, diagnostics, and cycle detection.
- `tests/engine/test_dependencies.py` — focused tests for field/metric propagation, invalidation, duplicate/unknown rules, cycles, and graph diagnostics.

## Verification

- Focused slice: `6 passed`, targeted coverage `99.37%`.
- Command: `python -m uv run --no-editable pytest tests\engine\test_dependencies.py --cov=engine.dependencies --cov-report=term-missing --cov-fail-under=90`
- Focused static checks: Ruff check and mypy strict green for `engine.dependencies` and its tests.
- Full local gates: Ruff format/check, mypy strict, agenda consistency, T-203/T-204 smoke, import-linter, and full pytest green. Full pytest result: `341 passed, 2 skipped`.

## Downstream notes

- T-502 should call `DependencyGraph.affected_by_fields(...)` when construct/session fields change and `affected_by_metrics(...)` when adapter metrics are refreshed.
- `DependencyImpact.traversal_order` is the same deterministic producer-before-consumer order as `affected_rules`.
- `DependencyCycleError` is intentionally raised before validation execution when produced metrics create a rule cycle.
