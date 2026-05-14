# T-606 Post-Execution Handover

## Status

Complete locally on 2026-05-14.

## Files Written

- `src/app/design_service.py`
- `tests/app/test_design_service_t606.py`
- `tasks/task_brief/T-606.md`
- `task_artefacts/T-606/post_execution.md`
- Status records in `README.md`, `ROADMAP.md`, `CODING_AGENDA.md`, and `TASK_BOARD.md`

## Implementation Notes

- Replaced the T-203 placeholder with `DesignService`.
- Added structural ports for the design event log, project session store, and session snapshot store so tests can use deterministic in-memory fakes.
- Implemented create/open/amend/compile/replay over `engine.session`.
- Added typed amendment payloads for parts, hosts, free text, LLM translation proposals/confirmations, rule acknowledgements, and override justifications.
- `compile_session` consults `GatePredicateRegistry` for `BlockCompile`; activated blocked gates prevent `DesignCompiled` from being appended.
- `current_pending_state(session_id)` maps replayed session states to phase-local pending steps:
  - `AwaitingScreening` → `BlockVendorSubmission`
  - `AwaitingAuthorisation` → `BlockOperationalProtocol`
  - `AwaitingSopRender` → `BlockOperationalProtocol`
  - `AwaitingExport` → `BlockExport`
- No screening, authorisation, SOP-rendering, or export services are stubbed or invoked by T-606.

## Verification

- Focused slice: `6 passed`.
- `ruff check src/app/design_service.py tests/app/test_design_service_t606.py`: passed.
- `mypy src/app/design_service.py tests/app/test_design_service_t606.py`: passed.
- `python tools/agenda_consistency_check.py`: passed.
- Full local pytest gate: `397 passed, 2 skipped`.

## Downstream Notes

- T-607 can consume `DesignService` to drive decision-tree events (`PartAdded`, `HostSelected`, `FreeTextEntered`) without depending on downstream screening or SOP/export services.
- T-1301 remains responsible for the full create → screen → authorise → export UAT path.
