# Cloning & Expression Vector Design Toolkit {version} Release Notes

Release date: {release_date}
Release documentation refreshed: 2026-05-15

## Scope

This release closes the v0.1.0 implementation agenda across {phase_count} ordered phases and
{active_task_count} active implementation task cards, ending at {final_task_id}.

## Highlights

- Deterministic white-paper UAT fixtures for bacterial, mammalian, and plant examples.
- Adversarial UAT coverage for authorisation, advisory, audit, plugin, export, replay, and IPC boundaries.
- A deterministic 100-realisation combinatorial-library benchmark with a 1000-realisation stretch fixture.
- Release build wrappers for the pinned container image and Python wheel.
- Traceability, risk-register, CI-gate, and task-board documentation aligned with the completed v0.1.0 line.
- React workspace refreshed with GMExpression branding, workflow-grade design summary, construct architecture table, compatibility matrix, validation report, advisory gate actions, and responsive layout polish.

## Verification

- `ruff check .`
- `mypy src tools tests`
- `python tools/ci/run_pytest.py -m "not slow"`
- `python -m pytest tests/uat/test_t1303_library_benchmark.py`
- `npm test` in `ui/`
- `npm run build` in `ui/`

## Safety

Generated outputs remain advisory. Screening, institutional authorisation, signed SOP-template
integrity, and export gates remain mandatory for operational use. The UI exposes design and
review state without bypassing institutional review, vendor screening, or professional judgement.
