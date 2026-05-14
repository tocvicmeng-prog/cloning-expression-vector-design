# Audit Key Runbook

## Purpose

The audit HMAC key protects the immutable `audit.sqlite` chain. It is an institutional log-integrity key, not a user/profile/decision-record signing key. Runtime code uses only the `AuditKeyProvider` methods: `mac`, `verify`, `verify_with_archived`, `rotate`, and `current_key_version`.

## Backends

Supported backend names:

- `file`: development-loop escrow JSON file. It emits a warning because key material is stored on disk.
- `windows_dpapi`: Windows production facade. In CI or unsupported runtimes it emits an explicit warning and falls back to the file escrow backend.
- `posix_keyring`: POSIX production facade. In CI or unsupported runtimes it emits an explicit warning and falls back to the file escrow backend.

The file escrow archive must be outside the `audit.sqlite` directory, protected by filesystem ACLs, and backed up with institutional secrets management. Every historical key version is retained indefinitely while any audit evidence may reference it.

## Provisioning

1. Select the backend through `config.audit_key_backend`.
2. Create the key archive path before first audit-service startup.
3. Restrict the archive path to the audit-service identity plus emergency escrow custodians.
4. Start the service and verify `current_key_version() == 1`.
5. Run `tools/audit_key_verifier.py --audit-db <audit.sqlite> --key-archive <archive.json>` after the first append.

## Rotation

Only `AdminPrincipal` or active `DeveloperBootstrapPrincipal` may rotate.

1. Produce a signed `DecisionRecord` for the rotation.
2. Call `AuditKeyRotationService.rotate(principal, reason=..., signed_decision_record=...)`.
3. Confirm the governance stream contains `AuditKeyRotated` with `key_version_before`, `key_version_after`, `rotation_reason`, and embedded decision payload.
4. Run the offline verifier against the current `audit.sqlite` and escrow archive.
5. Keep old key versions archived. Do not prune historical versions.

## Recovery

If `audit.sqlite` is intact but the current key archive is unavailable, restore the latest escrow backup and run the offline verifier. If any row IDs fail verification, treat the audit chain as compromised until an administrator review records the incident and recovery decision.

## Compromise Response

1. Stop audit-service writes.
2. Preserve `audit.sqlite`, the key archive, governance event logs, and filesystem metadata.
3. Rotate the audit key with an incident-response signed `DecisionRecord`.
4. Re-run offline verification and record failing row IDs, if any.
5. Re-enable writes only after the administrator review signs the recovery decision.

## Offline Verification

Run:

```powershell
python -m uv run --no-editable python tools\audit_key_verifier.py --audit-db path\to\audit.sqlite --key-archive path\to\audit-key.json
```

Exit codes:

- `0`: every row verifies.
- `1`: verifier failed before row verification or one or more row IDs failed verification.
