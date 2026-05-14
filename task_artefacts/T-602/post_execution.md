# T-602 Post-Execution Handover

## Status

verified locally

## Files written

- `src/engine/validation/predicates/metric_helpers.py` — metric/payload helper functions for pure predicates.
- `src/engine/validation/predicates/rbs.py` — MR-12 bacterial RBS spacing, TIR, and RNA accessibility predicate.
- `src/engine/validation/predicates/kozak.py` — MR-13 Kozak PWM threshold predicate.
- `src/engine/validation/predicates/uorf.py` — MR-14 uORF scan predicate.
- `src/engine/validation/predicates/premature_polya.py` — MR-15 premature polyadenylation motif predicate.
- `src/engine/validation/predicates/splice.py` — MR-16 splice-score threshold predicate.
- `src/engine/validation/predicates/cpg.py` — MR-27 CpG content predicate.
- `src/engine/validation/predicates/signal_peptide.py` — MR-28 signal peptide / compartment consistency predicate.
- `src/engine/validation/predicates/__init__.py` — added the T-602 predicate set to `IMPLEMENTED_PREDICATE_REGISTRY` only.
- `tests/engine/validation/test_biology_predicates_t602.py` — registry, metric-consumption, and fallback coverage.

## Verification

- Focused slice: `7 passed`, targeted coverage `89.89%`.
- Command: `python -m uv run --no-editable pytest tests\engine\validation\test_biology_predicates_t602.py --cov=engine.validation.predicates.rbs --cov=engine.validation.predicates.kozak --cov=engine.validation.predicates.uorf --cov=engine.validation.predicates.premature_polya --cov=engine.validation.predicates.splice --cov=engine.validation.predicates.cpg --cov=engine.validation.predicates.signal_peptide --cov=engine.validation.predicates.metric_helpers --cov-report=term-missing --cov-fail-under=85`
- Static checks: Ruff format/check and mypy strict green.
- CI support checks: agenda consistency, T-203/T-204 smoke, import-linter, and enforced `no-domain-impurity-check` green.
- Full local pytest gate: `387 passed, 2 skipped`.

## Downstream notes

- T-602 predicates do not import `adapter.biology`; they consume metric payloads through `ValidationContext`.
- `PREDICATE_REGISTRY` intentionally remains the Phase-4 stub registry. `IMPLEMENTED_PREDICATE_REGISTRY` now includes the T-503 structural subset plus the T-602 biology-dependent subset.
- T-603 should compute/cache the metric IDs used here, including `biology.rbs.*`, `biology.rna.mfe_kcal_mol`, `biology.kozak.score`, `biology.splice.*`, `biology.cpg.*`, and `biology.signal_peptide.has_signal_peptide`.
