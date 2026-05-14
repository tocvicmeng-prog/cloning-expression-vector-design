# SOP Template Signing Runbook

## Purpose

SOP-template signatures protect institutional procedure templates from silent modification. The SOP-template signing identity is independent of authorisation-profile signatures, decision-record signatures, and audit-log HMAC keys.

## Key Stores

- Purpose: `sop_template`
- Development archive path: operator-selected JSON file, commonly `keys/sop_template_signer/archive.json`
- Initial key version: `sop_template-ed25519-v1`
- Archive retention: indefinite for any key version referenced by a current or historical template

Do not reuse a `profile` or `decision_record` archive. The production adapters reject archives whose stored purpose does not match `sop_template`.

## Distribution

1. Require an `AdminPrincipal` or unexpired `DeveloperBootstrapPrincipal`.
2. Require a signed decision record documenting the reason.
3. Call `SopTemplateKeyManagementService.distribute_current_key(...)`.
4. Persist the emitted `SopTemplateSigningKeyDistributed` event in the governance stream.
5. Ensure engine processes load the updated public-key archive before accepting templates signed by that version.

## Rotation

1. Record the rotation decision as a signed decision record.
2. Call `SopTemplateKeyManagementService.rotate_key(...)`.
3. Distribute the emitted public-key fingerprint and new key version.
4. Keep the old key in the archive so historical templates remain verifiable.

## Revocation

1. Record the revocation decision and reason.
2. Call `SopTemplateKeyManagementService.revoke_key(...)`.
3. Confirm a `SopTemplateSigningKeyRevoked` governance event was appended.
4. Re-read affected SOP templates. A template signed by a revoked key must fail verification with `RevokedKeyError`.
5. Rotate a replacement key before minting or modifying templates.

## Offline Verification

Export a signed template with `sop_template_to_json(...)`, then run:

```powershell
python -m uv run --no-editable python tools\sop_template_signature_verifier.py --template-json path\to\sop-template.json --key-archive path\to\sop-template-keys.json
```

Expected success output:

```text
SOP-template signature valid
```

Failures print `SOP-template signature invalid: ...` and return exit code `1`.

## Compromise Response

1. Stop SOP-template mint/modify operations.
2. Revoke the compromised key with a signed decision record.
3. Rotate to a new key.
4. Re-sign active templates after administrative review.
5. Keep the revoked key in the archive for audit replay; verification must report revocation rather than unknown-key drift.
