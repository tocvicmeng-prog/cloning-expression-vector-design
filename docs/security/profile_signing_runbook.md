# Profile Signing Runbook

## Purpose

The profile-signing key is the institutional identity that signs `AuthorisationProfile` records. It is separate from the audit HMAC key and from per-principal decision-record keys.

## Provisioning

1. Create the profile signing archive path under admin-service-only storage.
2. Instantiate `Ed25519InstitutionalProfileSigner`; it creates the first Ed25519 key if none exists.
3. Distribute the public archive or public key material to verifier processes.
4. Verify a signed profile with `tools/profile_signature_verifier.py`.

## Rotation

Rotate with `Ed25519InstitutionalProfileSigner.rotate(reason, admin)`. Historical profiles remain verifiable through archived public keys unless a key is explicitly revoked.

## Revocation

Revoke a compromised key version with the archive-backed verifier or signer `revoke(...)` method. Existing profiles signed by that key then fail closed with `RevokedKeyError`.

## Offline Verification

```powershell
python -m uv run --no-editable python tools\profile_signature_verifier.py --profile-json path\to\profile.json --key-archive path\to\profile-keys.json
```

Exit `0` means the profile signature is valid. Exit `1` means the archive, payload, key version, revocation state, or signature failed verification.
