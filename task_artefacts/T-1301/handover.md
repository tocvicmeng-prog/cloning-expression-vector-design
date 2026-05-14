# handover/T-1301.md

## Status: verified

T-1301 white-paper-example UAT is complete locally.

## Files written

- `tests/uat/__init__.py`
- `tests/uat/helpers.py`
- `tests/uat/example_a_bacterial.py`
- `tests/uat/example_b_mammalian.py`
- `tests/uat/example_c_plant.py`
- `tests/uat/test_t1301_white_paper_examples.py`
- `tests/uat/fixtures/example_a/input_parts.json`
- `tests/uat/fixtures/example_a/host_context.json`
- `tests/uat/fixtures/example_a/scientific_advisor_signoff.json`
- `tests/uat/fixtures/example_a/expected_bundle_hash.txt`
- `tests/uat/fixtures/example_b/input_parts.json`
- `tests/uat/fixtures/example_b/host_context.json`
- `tests/uat/fixtures/example_b/scientific_advisor_signoff.json`
- `tests/uat/fixtures/example_b/expected_bundle_hash.txt`
- `tests/uat/fixtures/example_c/input_parts.json`
- `tests/uat/fixtures/example_c/host_context.json`
- `tests/uat/fixtures/example_c/scientific_advisor_signoff.json`
- `tests/uat/fixtures/example_c/expected_bundle_hash.txt`
- `tasks/task_brief/T-1301.md`

## Architecture sections consumed

- `ARCHITECTURE.md` v1.5 section 4.10 acceptance/UAT expectations
- Event-stream ownership for `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered`
- Safety-gate ordering for screening, authorisation, SOP rendering, and export

## Requirements satisfied

- AC-01..AC-03 white-paper worked-example UAT coverage
- UR-01a SnapGene file-watch fallback coverage
- Active advisory acknowledgement before authorisation
- Multi-host role-keyed compatibility for mammalian and plant examples

## CI gates touched

- No CI gate lifecycle was changed in this task.
- T-1301 supplies deterministic fixture hashes consumed by later release determinism work.

## Verification

- `$env:PYTHONPATH='src;.'; .\.venv\Scripts\python.exe -m pytest tests\uat\test_t1301_white_paper_examples.py -q` -> 3 passed
- `$env:PYTHONPATH='src;.'; .\.venv\Scripts\ruff.exe check tests\uat` -> passed
- `$env:PYTHONPATH='src;.'; .\.venv\Scripts\python.exe -m mypy src tests` -> passed, no issues in 520 source files
- `$env:PYTHONPATH='src;.'; .\.venv\Scripts\ruff.exe check .` -> passed
- `$env:PYTHONPATH='src;.'; .\.venv\Scripts\python.exe tools\ci\run_pytest.py -m "not slow" -q` -> 602 passed, 2 skipped

## Deferred / open

- T-1302 owns adversarial UAT and bypass scenarios.
- T-1303 owns library benchmark, release packaging, and container-level determinism enforcement.
