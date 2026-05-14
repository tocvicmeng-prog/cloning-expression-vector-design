# Decision Record Signing Runbook

## Purpose

Decision-record keys are per-principal Ed25519 identities. They bind a decision payload to the principal and key version that signed it. They are separate from institutional profile-signing keys and audit HMAC keys.

## Provisioning

1. Admin signs the key-lifecycle decision.
2. Call `DecisionRecordKeyManagementService.provision_principal_key(...)`.
3. Confirm the governance stream contains `DecisionRecordPublicKeyDistributed` with the public-key fingerprint and embedded signed decision payload.
4. Use `PerPrincipalDecisionRecordSigner` only after provisioning.

## Rotation

Call `rotate_principal_key(...)` on schedule or personnel change. Historical decision records continue verifying with archived public keys.

## Revocation

Call `revoke_principal_key(...)` for compromised credentials. The service emits `DecisionRecordPrincipalKeyRevoked`; verifiers fail closed for signatures made with that key version.

## Offline Verification

```powershell
python -m uv run --no-editable python tools\decision_record_verifier.py --signed-record-json path\to\signed-decision.json --key-archive path\to\decision-keys.json
```

Exit `0` means the signed decision record is valid. Exit `1` means the archive, key version, revocation state, principal binding, payload hash, or signature failed verification.
