# Admin Service IPC Contract

Task: T-1103a

This document defines the versioned contract implemented by the future
production admin-service IPC server in T-1103b and consumed by CLI/API code in
T-1101/T-1102 through `AdminServiceClientPort`.

## Protocol Version

`admin-service-ipc.v1`

Clients must send this value in every `AdminIpcRequest.protocol_version`.
Servers must return `version_mismatch` when they cannot support the requested
version.

## Framing

The production transport is local IPC:

- Windows: named pipe, final path specified by T-1103b.
- POSIX: Unix-domain socket, final path specified by T-1103b.

Frames are length-prefixed UTF-8 JSON:

```text
uint32_be_json_byte_length || canonical-json-compatible request bytes
```

The frame payload is the JSON object returned by
`AdminIpcRequest.to_payload()`. Responses use the same framing and the JSON
object returned by `AdminIpcResponse.to_payload()`.

## Authentication Envelope

Every request carries `principal_token`, a signed admin-principal token with:

- token id
- principal id
- principal role
- institution id
- issued/expires timestamps
- signing key version
- signature bytes as lowercase hex

T-1103a defines the envelope only. T-1103b verifies signatures using the
T-314a/T-314b `DecisionRecordVerifier` and production principal-key material.
Only `administrator` and pre-bootstrap `developer_bootstrap` roles are accepted
by the in-memory contract client; ordinary user, reviewer, and post-bootstrap
developer credentials are denied by production.

## Verbs

The contract exposes these verbs through `AdminServiceClientPort`:

- `mint_profile`
- `modify_profile`
- `revoke_profile`
- `list_profiles`
- `view_audit_trail`
- `mint_sop_template`
- `modify_sop_template`
- `revoke_sop_template`
- `triage_review_queue_item`
- `rotate_audit_key`

Each verb accepts the signed principal token plus a verb-specific payload. The
payload is a canonical-JSON-compatible object; binary signatures or files must
be encoded as lowercase hex or base64 strings by the caller.

## Response Shape

Accepted responses have:

- `status: "accepted"`
- verb-specific `payload`
- embedded signed decision record summary in `decision_record`

Denied/error responses have:

- `status: "denied"` or `status: "error"`
- `error_code`
- `error_message`
- optional diagnostic payload

Error codes in v1:

- `authentication_failed`
- `handler_error`
- `permission_denied`
- `unknown_verb`
- `validation_error`
- `version_mismatch`

## Deterministic Test Client

`tests.fakes.admin_service.InMemoryAdminServiceClient` implements
`AdminServiceClientPort` without IPC. It records every request, routes to
configurable in-memory handlers, wraps handler payloads with deterministic
signed decision-record metadata, and is intended for T-1101/T-1102 CLI/API unit
tests.
