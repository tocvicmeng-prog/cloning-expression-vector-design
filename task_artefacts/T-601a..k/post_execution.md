# T-601a..k Post-Execution Handover

## Status

verified locally

## Files written

- `src/adapter/biology/__init__.py` — package API replacing the T-203 placeholder module.
- `src/adapter/biology/common.py` — adapter manifests, sequence normalisation, content hashing, and shared payload helpers.
- `src/adapter/biology/vienna_rna.py` — deterministic `RnaFolder` implementation.
- `src/adapter/biology/spliceai.py` — deterministic `SplicePredictor` implementation.
- `src/adapter/biology/signalp.py` — deterministic `SignalPeptidePredictor` implementation.
- `src/adapter/biology/rbs_calc_v2.py` — deterministic `TIRPredictor` implementation.
- `src/adapter/biology/noderer_kozak.py` — deterministic `KozakScorer` implementation.
- `src/adapter/biology/{cai,minmax,charming,avoid_only}.py` plus `codon_support.py` — deterministic codon-algorithm adapters preserving translated protein and protected intervals.
- `tests/fakes/biology/` — fixture-driven deterministic fakes for all biology ports.
- `tests/calibration/biology/*/policy.yaml` — calibration drift policy files for every adapter.
- `tests/adapter/biology/test_biology_adapters.py` — adapter, fake, manifest, and policy coverage.

## Verification

- Focused slice: `8 passed`, targeted coverage `91.19%`.
- Command: `python -m uv run --no-editable pytest tests\adapter\biology tests\fakes\biology --cov=adapter.biology --cov=tests.fakes.biology --cov-report=term-missing --cov-fail-under=85`
- Static checks: Ruff format/check and mypy strict green.
- CI support checks: agenda consistency, T-203/T-204 smoke, import-linter, and enforced `no-domain-impurity-check` green.
- Full local pytest gate: `380 passed, 2 skipped`.

## Downstream notes

- The adapters are deterministic local implementations, not network clients. This is intentional for Phase 6 baseline reliability; optional heavyweight/service-backed implementations can be added behind the existing extras and port methods later.
- Every adapter exposes a manifest payload with local latency measurements and deterministic flags; T-603 can record these in metric provenance.
- T-602 can consume the metric payload shapes directly for MR-12, MR-13, MR-16, MR-28, CpG, and codon-dependent predicates.
