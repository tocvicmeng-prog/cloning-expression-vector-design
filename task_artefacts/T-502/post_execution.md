# T-502 Post-Execution Handover

## Status

verified locally

## Files written

- `src/engine/validation/validation_context.py` — picklable validation context, metric lookup, and stable SHA-256-derived predicate seeds.
- `src/engine/validation/report.py` — rule evaluation, typed error, deterministic report payload, canonical JSON, and content hash values.
- `src/engine/validation/engine.py` — pure DAG executor over `DependencyGraph`, incremental field/metric selection, predicate lookup, ordered aggregation, and HARD gate routing.
- `src/engine/validation/worker_pool_factory.py` — sequential, thread, and local-spawn process worker pools with submit-order result aggregation.
- `src/engine/validation/predicates/_stub.py` — top-level picklable stub predicates for registry transport.
- `tools/ci_gates/no_domain_impurity_check.py` — enforced static domain/engine import-boundary gate.
- `tests/engine/validation/` — focused T-502 executor and worker-pool tests.
- `tests/benchmark/T_502_validation_bench.py` and `tests/benchmark/results/T_502_validation_bench_local.json` — slow benchmark harness and first local result placeholder.

## Verification

- Focused slice: `11 passed, 1 deselected`, targeted coverage `91.98%`.
- Focused command: `python -m uv run --no-editable pytest tests\engine\validation tests\benchmark\T_502_validation_bench.py -m "not slow" --cov=engine.validation --cov=engine.dependencies --cov-report=term-missing --cov-fail-under=85`
- Static checks: Ruff format/check and mypy strict green.
- CI support checks: agenda consistency, T-203/T-204 smoke, import-linter, and enforced `no-domain-impurity-check` green.
- Full local pytest gate: `352 passed, 2 skipped`.

## Downstream notes

- Process workers use `multiprocessing.get_context("spawn")` locally and never call `set_start_method`; CLI/API entry points can still make their own process-policy decision later.
- `validate(...)` accepts `changed_fields` and/or `changed_metrics`; when neither is supplied it evaluates the full graph in deterministic topological order.
- Predicate failures are represented in `ValidationReport.errors`; callers should inspect `report.passed`, `report.blocked_gates`, and `report.errors` instead of catching predicate exceptions.
- T-503 should replace stubs with real predicates one rule family at a time while preserving top-level pickleability.
