# T-801 Post-Execution Notes

## Summary

Implemented `engine.risk_classification` as the Phase 8a active advisory-report generator. The module now parses validated `catalogues/risk_advisories.yaml` payloads into a typed catalogue, infers trigger tags from design metadata, emits severity-ordered `RiskAdvisoryReport` objects with graded citations, and binds `report_content_hash` to the session, construct, checksum, construct version, catalogue hash, and advisory payload.

## Files Changed

- `src/engine/risk_classification.py`
- `tests/engine/test_risk_classification_t801.py`
- `tasks/task_brief/T-801.md`
- `README.md`
- `ROADMAP.md`
- `CODING_AGENDA.md`
- `TASK_BOARD.md`

## Verification

- `python -m uv run --no-editable ruff check src/engine/risk_classification.py tests/engine/test_risk_classification_t801.py`
- `python -m uv run --no-editable mypy src/engine/risk_classification.py tests/engine/test_risk_classification_t801.py`
- `python -m uv run --no-editable pytest tests/engine/test_risk_classification_t801.py -q` -> 4 passed
- `python tools/agenda_consistency_check.py` -> passed
- `python -m uv run --no-editable ruff check .` -> passed
- `python -m uv run --no-editable mypy src tools tests` -> passed
- `python -m uv run --no-editable python tools/ci/run_pytest.py -m "not slow"` -> 447 passed, 2 skipped

## Next

Open T-802 `engine.design_plan`.
