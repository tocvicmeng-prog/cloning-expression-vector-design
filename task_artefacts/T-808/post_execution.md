# T-808 Post-Execution Notes

## Summary

Implemented `app.plugin_governance` as the signed plugin-manifest verification surface. The service loads manifest catalogues, verifies Ed25519 signatures against a trust keyring, checks artefact SHA-256 hashes, validates sandbox file/network permissions, emits approval/rejection governance events, and returns deterministic sandbox grants for approved plugins. The `plugin-manifest-signature` CI gate now runs in enforced mode over `catalogues/plugin_manifests`.

## Files Changed

- `src/app/plugin_governance.py`
- `tools/ci_gates/plugin_manifest_signature_check.py`
- `tests/app/test_plugin_governance_t808.py`
- `tests/ci_gates/test_t204_gates.py`
- `.github/workflows/ci.yaml`
- `catalogues/plugin_manifests/plugin_manifest_seed.yaml`
- `catalogues/plugin_manifests/artifacts/plugin.seed.txt`
- `schemas/plugin_manifests.schema.json`
- `tasks/task_brief/T-808.md`
- `README.md`
- `ROADMAP.md`
- `CODING_AGENDA.md`
- `TASK_BOARD.md`

## Verification

- `python -m uv run --no-editable ruff check src/app/plugin_governance.py tools/ci_gates/plugin_manifest_signature_check.py tests/app/test_plugin_governance_t808.py tests/ci_gates/test_t204_gates.py` -> passed
- `python -m uv run --no-editable mypy src/app/plugin_governance.py tools/ci_gates/plugin_manifest_signature_check.py tests/app/test_plugin_governance_t808.py tests/ci_gates/test_t204_gates.py` -> passed
- `python -m uv run --no-editable pytest tests/app/test_plugin_governance_t808.py tests/ci_gates/test_t204_gates.py -q` -> 10 passed
- `python -m uv run --no-editable python -m tools.ci_gates.plugin_manifest_signature_check --enforce` -> passed
- `python tools/agenda_consistency_check.py` -> passed
- `python -m uv run --no-editable ruff check .` -> passed
- `python -m uv run --no-editable mypy src tools tests` -> passed
- `python -m uv run --no-editable python tools/ci/run_pytest.py -m "not slow"` -> 476 passed, 2 skipped

## Next

Open T-901 `adapter.io` EMBL + GFF3 adapters.
