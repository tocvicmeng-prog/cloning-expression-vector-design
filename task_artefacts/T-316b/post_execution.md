# T-316b Post-Execution Handover

## Status

verified locally

## Files written

- `src/adapter/persistence/sqlite_sop_template_store.py` — signed SQLite SOP-template read/write/bootstrap store.
- `tests/adapter/persistence/test_sqlite_sop_template_store.py` — store, tamper, revocation, bootstrap, and idempotency tests.
- `tests/app/sop_template/test_admin_handler_sop_templates.py` — admin-handler SOP-template mint/modify/revoke and denial tests.

## Existing files updated

- `src/app/admin_action_handler.py` — added SOP-template mint/modify/revoke verbs with production signer integration, admin audit entries, and governance events.
- `src/domain/events/governance.py` — expanded SOP-template write events to carry signed template or revocation payloads.
- `src/adapter/persistence/__init__.py` and `docs/module_manifest.yaml` — exported/registered the SOP-template store.
- `catalogues/sop_templates/sop_template_seed.yaml` and `schemas/sop_templates.schema.json` — made bootstrap input structurally usable by `SopTemplate`.

## Verification

- Focused slice: `30 passed`, targeted coverage `90.82%`.
- Command: `python -m uv run --no-editable pytest tests\adapter\persistence\test_sqlite_sop_template_store.py tests\app\sop_template\test_admin_handler_sop_templates.py tests\security\sop_template_signing tests\domain\events\test_events.py --cov=adapter.persistence.sqlite_sop_template_store --cov=app.admin_action_handler --cov=adapter.security.sop_template_signing --cov=domain.events --cov-report=term-missing --cov-fail-under=85`
- Full local gates: Ruff format/check, mypy strict, agenda consistency, T-203/T-204 smoke, import-linter, and full pytest green. Full pytest result: `335 passed, 2 skipped`.

## Downstream notes

- Runtime reads should use `SqliteSopTemplateStore.get_template()` or `list_templates()` so signatures are verified before templates reach SOP rendering.
- Admin write paths should call `AdminActionHandler.mint_sop_template`, `modify_sop_template`, and `revoke_sop_template`; direct store writes bypass audit/governance events and should stay inside admin-service internals or tests.
- Bootstrap requires `signer`, `catalogue_dir`, and `schema_root` constructor arguments and returns only newly written versions; repeated unchanged bootstraps return an empty tuple.
