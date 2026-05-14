# T-603 Post-Execution Handover

## Status

verified locally

## Files written

- `src/app/validation_orchestrator.py` — validation metric pre-computation orchestrator, biology adapter injection, metric cache, predicate metric bindings, and pure validator invocation.
- `tests/app/test_validation_orchestrator_t603.py` — integration coverage for incremental affected-rule/metric re-evaluation, derivation-environment-bound cache reuse, and missing-adapter failure behavior.

## Verification

- Focused slice: `4 passed`.
- Command: `python -m uv run --no-editable pytest tests\app\test_validation_orchestrator_t603.py -q`
- Static checks: `python -m uv run --no-editable ruff check .` and `python -m uv run --no-editable mypy src tools tests` green.
- Agenda consistency: `python tools/agenda_consistency_check.py` green.
- Full local pytest gate: `391 passed, 2 skipped`.

## Downstream notes

- T-603 does not import concrete `adapter.biology` implementations; callers inject adapter ports through `BiologyAdapterSet`.
- Metric cache entries are keyed by session ID, derivation-environment hash, metric ID, and source fingerprint. A changed derivation environment forces recomputation even when biological inputs are unchanged.
- T-606 can call `ValidationOrchestrator.validate_design(...)` with the active rule registry and current design payload, then use the returned `ValidationReport` and affected-rule metadata for design-session state transitions.
