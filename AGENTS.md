# Codex Working Notes

This folder is the active Codex workspace for the cloning/expression vector design project.

Start every implementation or planning turn with:

1. Read `README.md`, `TASK_BOARD.md`, and the relevant `CODING_AGENDA.md` task card.
2. Run `python tools/agenda_consistency_check.py` before editing agenda/support docs.
3. Use `docs/task_manifest.yaml`, `docs/port_manifest.yaml`, and `docs/module_manifest.yaml` as the local machine-readable map. If a long-form document disagrees with a seed manifest, stop and fix the drift first.
4. Use `python -m uv sync --frozen --no-editable --group dev --extra io` and `python -m uv run --no-editable ...` for local checks; editable installs are intentionally avoided in this Windows/OneDrive/non-ASCII workspace.

Current source-of-truth order:

- Scientific/requirements truth: `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md`, then `REQUIREMENTS.md`.
- Architecture truth: `ARCHITECTURE.md`, amended by the v1.5 binding changes already propagated into `CODING_AGENDA.md`.
- Execution truth: `CODING_AGENDA.md` v1.5 plus `TASK_BOARD.md`.

For future Codex work:

- Keep edits scoped to the task card being executed.
- Update `TASK_BOARD.md` when task state changes.
- Update seed manifests when adding/removing/renaming task cards, canonical ports, or architecture modules.
- Do not revive removed runtime SOP-template library names or retired split-task IDs in active sections; the authoritative retired-ID set lives in `tools/agenda_consistency_check.py`.
- Admin mutations use `AdminPrincipal | DeveloperBootstrapPrincipal`; ordinary post-bootstrap `DeveloperPrincipal` is denied unless institutional policy explicitly grants permanent developer admin authority.
