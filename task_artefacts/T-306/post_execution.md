# T-306 Post-Execution Note

## Files Written

- `src/domain/types/design_plan/` non-operational design-plan values and runtime guard.
- `src/domain/types/controls/` control-design and control-set values.
- `src/domain/types/risk_advisory/` advisory, report, decision, and acknowledgement values.
- `src/domain/types/governance/` `DecisionRecord` and `RoleSnapshot` values.
- `src/domain/types/sop_protected/` operational protocol values, sentinel, DAG, hazard, and
  SOP-linked protocol types.
- `.importlinter` expanded with the `sop_protected` namespace partition contract.
- `tests/domain/types/test_t306/` namespace-boundary and invariant tests.
- `tasks/task_brief/T-306.md` refined with executable acceptance checks.

## Architecture and Requirement References

- `CODING_AGENDA.md` § 2.3.6 (`T-306`).
- `ARCHITECTURE.md` M11 and B-01 namespace separation.
- `REQUIREMENTS.md` FR-PROTO-DESIGN-03, FR-PROTO-SOP-10, FR-ADV-01..07, and BR-14 value-object
  prerequisites.

## Verification

- `python -m uv run --no-editable pytest tests\domain\types\test_t306 --cov=domain.types.design_plan --cov=domain.types.controls --cov=domain.types.risk_advisory --cov=domain.types.governance --cov=domain.types.sop_protected --cov-fail-under=85`:
  8 passed, 87.34% coverage.
- `python tools\agenda_consistency_check.py`: passed.
- `python -m uv run --no-editable ruff format --check .`: passed.
- `python -m uv run --no-editable ruff check .`: passed.
- `python -m uv run --no-editable mypy src tools tests`: passed.
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"`:
  120 passed, 2 skipped.
- `python -m uv run --no-editable lint-imports --config .importlinter`: 3 contracts kept.

## Downstream Notes

T-307 still owns RFC 8785/JCS canonicalisation and `DerivationEnvironment`. T-306 deliberately uses
plain frozen value objects and local invariants; canonical byte-level hashing remains in T-307.
