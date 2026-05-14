# T-316c Post-Execution Handover

## Status

verified locally

## Files written

- `src/adapter/security/sop_template_signing/` — Ed25519 signer, verifier, JSON serialization, and package exports.
- `src/app/sop_template_key_management.py` — institutional SOP-template signing-key distribution, rotation, and revocation service.
- `tools/sop_template_signature_verifier.py` — standalone offline verifier.
- `docs/security/sop_template_signing_runbook.md` — operational key lifecycle and compromise response runbook.
- `tests/security/sop_template_signing/` — production signing, tamper, key-version, revocation, offline verifier, and identity-separation tests.

## Existing files updated

- `src/adapter/security/signing_key_archive.py` — added the `sop_template` archive purpose.
- `src/domain/events/governance.py` and `src/domain/events/__init__.py` — added `SopTemplateSigningKeyDistributed` and `SopTemplateSigningKeyRevoked`.
- `src/domain/security/authorisation_profile.py`, `src/domain/types/review_queue.py`, and `src/domain/types/__init__.py` — narrowed imports to break a package import cycle exposed by non-editable installs.
- `docs/module_manifest.yaml` — registered T-316c source modules.

## Verification

- Focused slice: `22 passed`, targeted coverage `93.13%`.
- Command: `python -m uv run --no-editable pytest tests\security\sop_template_signing tests\domain\events\test_events.py tests\domain\ports\test_sop_template_contract.py --cov=adapter.security.sop_template_signing --cov=app.sop_template_key_management --cov=adapter.security.signing_key_archive --cov=domain.events --cov-report=term-missing --cov-fail-under=85`

## Downstream notes

- T-316b should inject `Ed25519InstitutionalSopTemplateSigner` into bootstrap/admin-write paths and `Ed25519InstitutionalSopTemplateVerifier` into read-side verification.
- The canonical development key version is `sop_template-ed25519-v1`; profile and decision-record archives intentionally reject this purpose.
- Runtime SOP-template JSON interchange for the offline verifier is available via `sop_template_to_json` / `sop_template_from_json`.
