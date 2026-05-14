# Cloning Expression Vector Design {version} Release Notes

Release date: {release_date}

## Scope

This release closes the v0.1.0 implementation agenda across {phase_count} ordered phases and
{active_task_count} active implementation task cards, ending at {final_task_id}.

## Highlights

- Deterministic white-paper UAT fixtures for bacterial, mammalian, and plant examples.
- Adversarial UAT coverage for authorisation, advisory, audit, plugin, export, replay, and IPC boundaries.
- A deterministic 100-realisation combinatorial-library benchmark with a 1000-realisation stretch fixture.
- Release build wrappers for the pinned container image and Python wheel.

## Verification

- `ruff check .`
- `mypy src tools tests`
- `python tools/ci/run_pytest.py -m "not slow"`
- `python -m pytest tests/uat/test_t1303_library_benchmark.py`

## Safety

Generated outputs remain advisory. Screening, institutional authorisation, signed SOP-template
integrity, and export gates remain mandatory for operational use.
