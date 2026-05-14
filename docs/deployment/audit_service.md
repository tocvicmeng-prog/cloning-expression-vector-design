# Audit Service Deployment Runbook

## Purpose

The audit service is the only production writer for `audit.sqlite`. Engine and admin-service processes append through IPC clients implementing `AuditAppendPort` and `AdminAuditAppendPort`.

## Startup

1. Provision the audit HMAC key archive from T-312b.
2. Provision decision-record public keys from T-314b so IPC caller tokens can be verified.
3. Start the audit-service process with the `audit.sqlite` path, key archive, decision-record key archive, governance-event directory, and IPC endpoint.
4. On startup, the service opens `audit.sqlite`, creates the schema if needed, and verifies the existing HMAC chain before accepting appends.

## IPC

The current implementation uses framed JSON requests. Production deployment maps the same request/response contract to:

- Windows named pipe: `\\.\pipe\cev-audit-service`
- POSIX Unix socket: `/var/run/cev-audit/socket`

Clients retry timeout failures and raise `AuditServiceUnreachableError` after the configured retry budget.

## Authentication Failure

Invalid or mismatched signed caller tokens are rejected. The audit row is not appended. The audit service writes `AuditServiceAuthenticationFailed` to the governance stream through its minimal local governance writer.

## Recovery

After a crash, restart the audit service with the same `audit.sqlite` and key archive. The writer verifies the existing chain before accepting new rows. If verification fails, keep the service offline and run `tools/audit_key_verifier.py` to identify failing row IDs.
