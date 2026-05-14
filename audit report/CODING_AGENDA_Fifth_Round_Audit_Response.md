# Fifth-Round CODING_AGENDA.md Audit Response

**Date:** 2026-05-14  
**Responding document set:** `CODING_AGENDA.md` v1.5, `ARCHITECTURE.md` v1.5 amendments, `REQUIREMENTS.md` amendments, `ROADMAP.md` v1.5, `TASK_BOARD.md` v1.5, `README.md`, `AGENTS.md`, `docs/*_manifest.yaml`, `tools/agenda_consistency_check.py`.

## Executive Disposition

All 25 fifth-round findings are accepted. No defenses are raised.

The fifth-round audit correctly identified that v1.4 was a partial synchronization draft rather than a coding-ready plan. The v1.5 response is a mechanical consistency release: it fixes build order, active task identity, counts, port arithmetic, Section 3 wiring, source-document authority, support-doc drift, and Codex handoff guardrails before implementation starts.

## Finding Resolution

| Finding | Disposition | Resolution |
|---|---|---|
| B5-01 Phase 3 physical heading order | Accepted | Phase 3 active task cards now follow the executable dependency order: early Protocol/fake tasks before consumers, production auth/signing tasks after T-311, production audit service after production profile verifier. |
| B5-02 stale unsplit T-314 card | Accepted | The stale active card was removed. The active Section 2 count is 71 after deletion. |
| B5-03 phase/cumulative counts | Accepted | Phase 3 is 19 tasks, Phase 4 is 8 tasks, and the active Section 2 total is 71. Counts are encoded in `docs/task_manifest.yaml` and checked by `tools/agenda_consistency_check.py`. |
| B5-04 port inventory | Accepted | The canonical port inventory is re-enumerated to 50 unique ports with `docs/port_manifest.yaml` as the seed manifest. |
| B5-05 composition root | Accepted | Section 3 now wires `SopProtocolGenerator(sop_template_read_port)` and removes the undefined SOP-template library variable from runtime composition. |
| B5-06 audit-service verifier dependency | Accepted | T-314b now precedes T-313b, so production audit-service authentication can consume the production verifier. |
| B5-07 SOP-template signer dependency | Accepted | T-316c now precedes T-316b, so signed SQLite bootstrap consumes the production SOP-template signer/verifier. |
| B5-08 split-task consumer references | Accepted | T-310, T-311, T-315, T-803, T-903, and admin-service cards now refer to split responsibilities instead of unsplit legacy tasks. |
| B5-09 review-queue admin triage | Accepted | `ReviewQueueAdminPort` is a T-315 deliverable and admin triage routes through admin-service IPC. |
| B5-10 source-of-truth hierarchy | Accepted | `ARCHITECTURE.md` and `REQUIREMENTS.md` now carry the v1.5 authority for signed SOP-template ports, `DeveloperBootstrapPrincipal`, `interface.audit_service`, and `interface.admin_service`. |
| H5-01 stale-token gate scope | Accepted | `tools/agenda_consistency_check.py` checks active agenda sections plus support-doc active text for retired IDs and stale authority markers. |
| H5-02 task-board regeneration | Accepted | `TASK_BOARD.md` is regenerated to v1.5 counts and points at the seed manifests/checker. |
| H5-03 missing manifests | Accepted | `docs/task_manifest.yaml`, `docs/port_manifest.yaml`, and `docs/module_manifest.yaml` are committed as bootstrap manifests. |
| H5-04 audit-service auth failure | Accepted | T-313b owns `AuditServiceAuthenticationFailed` governance-event writing without circular engine-service IPC. |
| H5-05 admin-service IPC auth ownership | Accepted | T-1103b authentication now depends on the production verifier from T-314b. |
| H5-06 unsigned profile draft | Accepted | T-304 adds `UnsignedAuthorisationProfileDraft`; T-311 signs only canonical validated drafts. |
| H5-07 module coverage | Accepted | `docs/module_manifest.yaml` includes `interface.audit_service`, `interface.admin_service`, and the v1.5 security/admin modules. |
| H5-08 no-self-authorisation gate | Accepted | The authoritative CI lifecycle table names the six security surfaces and v1.5 owning tasks. |
| H5-09 README/ROADMAP drift | Accepted | README and ROADMAP now advertise v1.5 agenda authority and current source-document hierarchy. |
| M5-01 range notation | Accepted | `T-601a..k` remains one active card and is explicitly expanded in `docs/task_manifest.yaml`. |
| M5-02 Section 2 numbering | Accepted | Phase 8a headings are parser-visible as `2.8a.*`; duplicate section/ID checks are enforced. |
| M5-03 sign-off overstatement | Accepted | Final sign-off is conditional on `python tools/agenda_consistency_check.py` remaining green. |
| M5-04 audit-key retention | Accepted | Audit-key retention language now requires indefinite escrow for keys needed by historical verification. |
| M5-05 font reproducibility wording | Accepted | T-201 uses future-tense committed-font wording; it no longer claims fonts already exist in the repository. |
| M5-06 Windows/OneDrive fixtures | Accepted | T-205 includes named-pipe, Unix-socket, and OneDrive SQLite WAL/platform fixtures. |

## Verification

`python tools/agenda_consistency_check.py` passes with:

```text
agenda consistency check passed: 71 active task headings, 50 canonical ports
```

The checker also validates seed-manifest presence/order/counts, port-manifest uniqueness, required source-document markers, active stale-token scope, and the Codex working-folder root.
