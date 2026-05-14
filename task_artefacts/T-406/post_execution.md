# T-406 Post-Execution Record

## Summary

Populated the policy/profile catalogues that downstream screening, export, advisory, and vendor-adapter tasks consume.

- Replaced seed vendor profiles for Twist, IDT, and GenScript with structured service, sequence-constraint, submission, screening, and citation metadata.
- Replaced `screening_trust_policy.yaml` with provider trust defaults for IGSC v3, IBBIS Common Mechanism, SecureDNA, and institutional blacklist adapters.
- Replaced `institutional_policy.yaml` with administrator-controlled authorisation, asymmetric reviewer/admin, dual-control, unsupported BSL-4, and active advisory acknowledgement defaults.
- Replaced `export_profiles.yaml` with internal audit, vendor submission, public redacted sharing, and regulatory/IBC review profiles.
- Replaced `risk_advisories.yaml` with active caution/strong-caution advisories tied to gate blocks and acknowledgement policy.
- Tightened the T-406 JSON Schemas and added regression tests for sentinel IDs, vendor limits, verdict behavior, redaction boundaries, and advisory acknowledgement requirements.

## Verification

- Focused T-406 catalogue/gate slice: `36 passed`, 91.56% coverage.
- Static gates before documentation update: Ruff format/check and mypy green.
- Agenda consistency and manifest smoke checks green.
- Full static gates: Ruff format/check, mypy, import-linter green.
- Full pytest: `315 passed, 2 skipped`.

## Handoff

T-316c is next: implement production SOP-template signer/verifier adapters and key lifecycle before T-316b consumes them during signed SOP-template bootstrap.
