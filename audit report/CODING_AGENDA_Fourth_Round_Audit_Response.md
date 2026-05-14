# Fourth-Round CODING_AGENDA.md Audit — Three-Role Response

**Audit input:** `audit report/CODING_AGENDA_Fourth_Round_Audit_Report.md`.
**Subject:** `CODING_AGENDA.md` v1.3.
**Result:** **27 / 27 findings accepted (9 blocking + 10 high + 8 moderate); 0 defended.**
**Output:** `CODING_AGENDA.md` v1.4; `ROADMAP.md` regenerated; `TASK_BOARD.md` regenerated; `README.md` updated; memory pointer updated.
**Adjudicating roles:** `/architect`, `/scientific-advisor`, `/dev-orchestrator`.
**Date:** 2026-05-14.

## Executive summary

The auditor's verdict is correct. v1.3 introduced the right primitives (AuditAppendPort, profile signing, signed SOP-template storage, review queue, DeveloperBootstrapPrincipal, admin-service IPC) but propagated them as **task cards** without (a) physically reordering the module catalogue, (b) re-scheduling the new tasks to land before their consumers, (c) regenerating Section 3 wiring, (d) producing an executable audit-concurrency model, and (e) updating the dependent CI gates, port inventory, manifest authority, and supporting docs. The drift pattern v1.2/v1.3 fought has reappeared in a more subtle form: the task-card layer is consistent with itself, but the build queue, wiring, and QC layer remain v1.2.

The three roles convened, walked each finding against `ARCHITECTURE.md` v1.5, `REQUIREMENTS.md` (FR-AUTH-04/09/14, BR-12, FR-PROTO-SOP-09), and the v1.3 wiring, and accepted every finding without defence. v1.4 is a **synchronisation + executability pass**: physically reorder Section 2, split new infrastructure tasks so protocols/fakes land before consumers, redesign the audit-concurrency model into a single executable writer, regenerate Section 3, and align supporting docs.

| Severity | Total | Accepted | Defended |
|---:|---:|---:|---:|
| Blocking | 9 | 9 | 0 |
| High | 10 | 10 | 0 |
| Moderate | 8 | 8 | 0 |

## Blocking findings

### B4-01 — Section 2 physical heading order disagrees with binding phase order. **Accepted.**

**Adjudication.** v1.3 declares phase order `9a → 10 → 8b → 9b` but Section 2 physically places `Phase 9a → Phase 8b → Phase 9b → Phase 10`. `task_manifest_generator.py` emits task IDs in heading order, so the generated manifest would put `T-803 / T-805b / T-806b / T-903` before `T-1001 / T-1002` — reopening the v1.1 / v1.2 screening-before-SOP safety defect at the manifest layer.

**v1.4 correction.** Physically move the Phase 10 section in CODING_AGENDA.md § 2 so it appears between `Phase 9a` and `Phase 8b`. Final order in Section 2: Phase 2 → 3 → 4 → 5 → 6 → 7 → 8a → 9a → **10** → 8b → 9b → 11 → 12 → 13. Also add an explicit phase-order table to `task_manifest_generator.py` so any future heading-order regression fails CI. Add a CI fixture `tests/ci_gates/test_task_manifest_phase_order.py` that asserts `T-1001 / T-1002` precede `T-803 / T-806b / T-903` in `docs/task_manifest.yaml`.

### B4-02 — T-314 scheduled after consumers. **Accepted.**

**Adjudication.** T-310d / T-311 consume `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` (and DecisionRecordSigner — cross-resolution with B4-09). T-314 was scheduled later in Phase 3. Cannot pass acceptance.

**v1.4 correction.** Split T-314 into:

- **T-314a** (Phase 3, scheduled immediately after T-307 / T-312a, before T-308) — `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` Protocols + deterministic test signer/verifier + signature error taxonomy + `DecisionRecordSigner` Protocol + test signer (B4-09 cross-resolution). Sonnet, ≤ 30 k tokens.
- **T-314b** (Phase 3, after T-311) — production institutional-signer adapter + production per-principal `DecisionRecordSigner` adapter + key lifecycle (rotation, archive, revocation, offline verifier, public-key distribution, compromised-key response). Opus, ≤ 55 k tokens.

T-310d / T-311 depend on T-314a only.

### B4-03 — T-313 scheduled after consumers. **Accepted.**

**Adjudication.** T-310c / T-311 reference `AuditAppendPort` (engine broker) + `AdminAuditAppendPort` (admin handler), both from T-313. T-313 scheduled later. Acceptance unprovable.

**v1.4 correction.** Split T-313 into:

- **T-313a** (Phase 3, scheduled immediately after T-312a, before T-308) — `AuditAppendPort` + `AdminAuditAppendPort` Protocols + `ServicePrincipal` type + deterministic in-memory fake brokers + chain-integrity test helpers + service-principal registry contract. Sonnet, ≤ 30 k tokens.
- **T-313b** (Phase 3, after T-311; redesigned per B4-04) — production single-writer audit-service broker. Opus, ≤ 55 k tokens.

T-310c / T-311 depend on T-313a only (for the Protocol + chain-integrity test helpers used in their HMAC-chain tests).

### B4-04 — Dual-writer audit-lock model non-executable. **Accepted.**

**Adjudication.** Engine `AuditBroker` and admin-service `AdminActionHandler` cannot both hold a lifetime exclusive `mode=rw` lock on `audit.sqlite`. The v1.3 "lock-handoff protocol" was named but undefined. Cross-process coordination on a single SQLite chain requires a single physical writer or a documented coordination protocol with state machine, timeout, and recovery.

**v1.4 correction.** Adopt a **single audit-service writer** model:

- A dedicated **audit-service process** (separate from both the engine process and the admin-service process) owns the `mode=rw` lock on `audit.sqlite` for its lifetime. Both engine and admin-service processes send append requests over IPC (named pipe on Windows, Unix socket on POSIX). The audit-service process serialises all appends through a single in-process queue, computes the HMAC chain, and persists each row atomically.
- The audit-service exposes two IPC verbs: `engine_append(entry, service_principal_token)` and `admin_append(entry, admin_principal_token)`. The token (signed via `DecisionRecordSigner` from T-314a) authenticates the caller; the audit-service validates the token before appending.
- `AuditAppendPort` and `AdminAuditAppendPort` (T-313a) become **IPC client ports**; the broker (T-313b) is the IPC client + server implementation.
- Acceptance tests for T-313b: concurrent engine+admin appends under load produce a single linear HMAC chain (no interleaving corruption); audit-service crash recovery (re-open `audit.sqlite`, recompute last HMAC, accept new appends); IPC timeout behaviour (engine blocks for max 5s on append, retries with backoff); key-rotation during concurrent appends produces a clean chain transition.
- Persistence-table update: `audit.sqlite` writer is **`audit-service process`** only; engine + admin-service hold IPC client handles.

### B4-05 — T-316 bootstrap before YAML inputs exist + composition root still uses YAML loader. **Accepted.**

**Adjudication.** T-316 was Phase 3; its bootstrap reads `catalogues/sop_templates/*.yaml`. But the SOP-template JSON schema lands in T-401 (Phase 4); the YAML files themselves are populated in T-406 (Phase 4). T-316 bootstrap is unrunnable in Phase 3. Separately, the composition root still constructs `sop_template_library: SopTemplateLibrary = YamlSopTemplateLoader(...).load()` and feeds it to `SopProtocolGenerator`, even after the new `SopTemplateReadPort` is in scope — runtime keeps the old surface alive.

**v1.4 correction.** Split T-316 into:

- **T-316a** (Phase 3, after T-314a) — ports + value objects only: `SopTemplateReadPort` / `SopTemplateAdminWritePort` / `SopTemplateBootstrapPort` Protocols + `SopTemplateSigner` / `SopTemplateVerifier` Protocols (with deterministic test signer/verifier per H4-04) + value-object types (`SopTemplate`, `SopTemplateSignature`, `SopTemplateVersion`). Sonnet, ≤ 35 k tokens.
- **T-316b** (Phase 4, after T-406 catalogue population) — signed SQLite store + bootstrap migration + signature verification + admin-write handler extension + governance events. Opus, ≤ 55 k tokens.

Remove `sop_template_library: SopTemplateLibrary` and `YamlSopTemplateLoader` from the composition root entirely. `SopProtocolGenerator` (T-803) consumes `sop_template_read_port: SopTemplateReadPort` only.

### B4-06 — Section 3 wiring stale (v1.2 terminology). **Accepted.**

**Adjudication.** Section 3 header says "v1.2"; DAG references `T-309a` / `T-309b` / unsplit `T-312`; persistence text still mentions `SopTemplateLibrary` admin-writable via T-803; composition root says "admin commands wire to T-311 AdminActionHandler" instead of routing via T-1103 IPC. Section 3 is the executable wiring blueprint; if it disagrees with task cards, implementers will follow the wiring not the cards.

**v1.4 correction.** Regenerate § 3 end-to-end for v1.4:

- § 3 header: "v1.4 — synchronised with task catalogue".
- § 3.1 DAG: phase order `8a → 9a → 10 → 8b → 9b`; remove all `T-309a` / `T-309b` references (use single `T-309`); remove unsplit `T-312` (use `T-312a` / `T-312b`); add new tasks (T-313a/b, T-314a/b, T-315, T-316a/b, T-1103a/b).
- § 3.2 composition root: remove `YamlSopTemplateLoader`; remove `audit_log: AuditLog` direct construction; replace with `audit_append: AuditAppendPort = AuditServiceClient(...)` (IPC client); inject `sop_template_read_port: SopTemplateReadPort = SqliteSopTemplateStoreRead(...)`; inject `decision_record_signer: DecisionRecordSigner = config.decision_record_signer()` constructed via T-314b adapter.
- § 3.3 event-stream wiring: unchanged structurally (v1.3 B3-03 embedded payloads remain).
- § 3.4 persistence wiring: `audit.sqlite` writer = **audit-service process** (single physical writer per B4-04); engine + admin-service hold IPC client handles. `sop_templates.sqlite` writer = admin-service-process via T-316b.
- § 3.5 CI lifecycle table: expand security-gate scope per H4-02.
- Add static check `tests/ci_gates/test_no_stale_task_ids_in_active_sections.py` that fails if `T-309a`, `T-309b`, or unsplit `T-312` appear in active sections (allowed only in `7.4b` / `7.4c` / `7.4d` historical sections + Appendix A).

### B4-07 — Manifest-driven module coverage requires architecture anchors that don't exist. **Accepted.**

**Adjudication.** T-204's `architecture_manifest_generator.py` parses `ARCHITECTURE.md` § 4.2 by anchor markers `<!-- module: <id> -->`. No such anchors are present. `ARCHITECTURE.md` § 4.2 also predates v1.3 module additions (AuditAppendPort, AuthorisationProfileSigner, ReviewQueueStore, SopTemplate split ports, interface.admin_service).

**v1.4 correction.** Change manifest authority:

- `docs/module_manifest.yaml` is **manually authored** (committed by `/dev-orchestrator`); `tools/architecture_manifest_generator.py` is removed from T-204 v1.4.
- The manifest's schema becomes the binding source for module-coverage CI; `ARCHITECTURE.md` § 4.2 is treated as a **checked reference** (a separate static check `tests/ci_gates/test_architecture_manifest_consistency.py` warns if a module appears in the manifest but is not referenced anywhere in `ARCHITECTURE.md` — informational only).
- T-204's deliverables update: `docs/module_manifest.yaml` (committed manifest with the v1.3/v1.4 surface) replaces the generator script.
- An optional **architecture-amendment task T-104** is added in Phase 1 (or as a v1.6 architecture pass after coding starts) to insert stable module anchors. Until that runs, the agenda's module manifest is canonical.
- `module_coverage_check.py` parses the manually-authored `docs/module_manifest.yaml`; the test passes when every entry has ≥ 1 declared task in `docs/task_manifest.yaml`.

### B4-08 — Admin-service IPC introduced after CLI/API consumers. **Accepted.**

**Adjudication.** Phase 11 order was `T-1101 (CLI) → T-1102 (API) → T-1103 (admin-service IPC)`. T-1101 includes admin commands; T-1102 says admin endpoints route via T-1103. Without T-1103 first, implementers wire CLI/API directly to `AdminActionHandler`.

**v1.4 correction.** Split T-1103 into:

- **T-1103a** (Phase 11, **before T-1101 / T-1102**) — `AdminServiceClientPort` Protocol + IPC contract definition (named pipe path + socket path + verbs + framing format + signed-token authentication) + deterministic in-memory test client + acceptance tests for the contract. Sonnet, ≤ 35 k tokens.
- **T-1103b** (Phase 11, after T-1101 / T-1102) — admin-service process executable + IPC server + OS-level ACL/UID enforcement (M4-05 cross-resolution) + ReviewQueueAdminPort (H4-01 cross-resolution) + integration with T-1101 / T-1102 admin commands. Opus, ≤ 60 k tokens.

T-1101 / T-1102 acceptance: admin commands construct an `AdminServiceRequest` and dispatch via `AdminServiceClientPort`; static check fails if they import `AdminActionHandler` directly.

### B4-09 — `DecisionRecordSigner` has no concrete implementation/key lifecycle owner. **Accepted.**

**Adjudication.** `DecisionRecordSigner` is consumed by admin actions, review queue decisions, advisory acknowledgement, screening sign-off, admin-service authentication. No task owned the production adapter, keystore, rotation policy, public-key distribution, or compromised-key response.

**v1.4 correction.** Extend T-314 split (per B4-02) to cover `DecisionRecordSigner`:

- **T-314a** adds: `DecisionRecordSigner` Protocol + `DecisionRecordVerifier` Protocol + deterministic test signer/verifier + per-principal signing contract.
- **T-314b** adds: production per-principal asymmetric signer adapter (Ed25519); per-principal key provisioning (signed by institutional admin); key rotation (per-principal); revocation list; offline `decision_record_verifier.py` tool; public-key distribution to engine processes; compromised-key response runbook; adversarial tests (`test_decision_record_signature_verifier`, `test_revoked_principal_signature_fails`, `test_rotated_principal_key_verifies_historical_records`).

## High findings

### H4-01 — Review-queue admin triage not wired into admin-service IPC. **Accepted.**

**v1.4 correction.** Define `ReviewQueueAdminPort` (admin-service-side) in T-315; inject into T-1103b admin-service constructor; add IPC verb `triage_review_queue_item(admin_principal_token, item_id, decision)`; T-315 acceptance test `test_user_or_api_cannot_resolve_own_request` confirms user-side callers cannot bypass the admin IPC.

### H4-02 — Security CI gates stale + narrow. **Accepted.**

**v1.4 correction.** Expand `no-self-authorisation-check` to cover:

- UserPrincipal **and ReviewerPrincipal** attempts (FR-AUTH-14);
- `SopTemplateAdminWritePort` writes;
- `AuditAppendPort` / `AdminAuditAppendPort` callable surface;
- direct CLI/API reachability to `AdminActionHandler` (must route via `AdminServiceClientPort`);
- admin-service IPC bypass attempts;
- `DeveloperBootstrapPrincipal` post-bootstrap restrictions.

Split activation milestones:

- `informational` after T-311 (initial admin handler scope).
- `enforced` only after T-313b + T-316b + T-1103b all verified.
- `enforced-green` requires all six surfaces covered by adversarial tests.

Add three new CI gates:
- `no-direct-admin-handler-import-check` — static: CLI/API code paths must not import `AdminActionHandler`.
- `audit-append-port-only-check` — static: engine-process governance services must not import `SqliteAuditLog` or `AuditBroker` directly; must use `AuditAppendPort`.
- `sop-template-admin-port-only-check` — static: SOP rendering / catalogue loaders must not import the admin-write port.

### H4-03 — Task-acceptance gate has no path to create initial briefs. **Accepted.**

**v1.4 correction.** Extend T-204 with a deliverable `tools/initial_task_brief_generator.py` that walks `CODING_AGENDA.md` § 2 task headings and emits initial `tasks/task_brief/T-<id>.md` files (with the mandatory YAML acceptance block per M3-03 / Appendix D). Initial briefs are *seeds*; `/dev-orchestrator` refines each brief before assignment. Add a manifest test `tests/ci_gates/test_task_brief_coverage.py` that asserts every `#### ... T-*` heading has a corresponding brief file.

### H4-04 — SOP-template signing key lifecycle underspecified. **Accepted.**

**v1.4 correction.** Add to port inventory: `SopTemplateSigner` (#46) + `SopTemplateVerifier` (#47). Add a new task **T-316c** (Phase 4, after T-316b) — production institutional SOP-template signer + verifier adapters; key versioning + archive + revocation list + offline `sop_template_signature_verifier.py` tool + public-key distribution + compromised-key response. Sonnet, ≤ 35 k tokens. T-316a ships the Protocols + test signer/verifier; T-316b consumes them; T-316c adds the production adapters.

### H4-05 — Audit-key archive can break long-term verification. **Accepted.**

**v1.4 correction.** Update T-312b: audit-key archive retention is **indefinite** for any key version referenced by an audit row. The bounded `N=10` rolling archive is removed. Archive is stored in an external escrow location (institutionally-controlled; documented in `docs/security/audit_key_runbook.md`); the in-process keystore retains the **current** key + the most recent rotation; verification queries to the escrow archive go through `AuditKeyProvider.verify_with_archived(key_version, ...)` which transparently fetches archived keys from escrow when not in the in-process archive. Test `test_audit_verification_after_eleven_rotations` confirms historical rows still verify after the in-process archive eviction window.

### H4-06 — REQUIREMENTS + ARCHITECTURE conflict with `DeveloperBootstrapPrincipal`. **Accepted.**

**v1.4 correction.** Add to agenda § 0.3 a paragraph noting that source-doc references to `DeveloperPrincipal` in admin-mint / admin-modify / admin-revoke contexts (FR-AUTH-04/09, BR-12, ARCHITECTURE permissions matrix) are interpreted as `DeveloperBootstrapPrincipal` under v1.3 H3-10 / v1.4. Add tests: `test_developer_principal_without_bootstrap_claim_denied_post_bootstrap` + `test_requirements_and_architecture_developer_principal_references_documented`. Schedule a v1.6 source-doc amendment pass (separate from this audit response) to update REQUIREMENTS / ARCHITECTURE text directly.

### H4-07 — ROADMAP not truly regenerated. **Accepted.**

**v1.4 correction.** Regenerate active sections of `ROADMAP.md`: remove remaining `ARCHITECTURE.md v1.1` citations (replace with v1.5); remove `SopTemplateLibrary` references (use `SopTemplateReadPort`); remove `DeveloperPrincipal` admin references (use `DeveloperBootstrapPrincipal`); remove `T-309b` (single T-309 identity). Add stale-token CI check `tests/ci_gates/test_roadmap_stale_tokens.py`.

### H4-08 — Task-board and Appendix C arithmetic drift. **Accepted.**

**v1.4 correction.** Replace hand-edited counts with manifest-derived counts. `TASK_BOARD.md` § 1 cumulative count line is generated by `tools/task_count_reporter.py` (from `docs/task_manifest.yaml`). Appendix C T-805 row removed (already noted in v1.3 H3-07; v1.4 confirms the row is physically absent). Add CI assertion `tests/ci_gates/test_task_count_consistency.py` that confirms heading-count + Appendix C row-count + TASK_BOARD § 1 count agree.

### H4-09 — PDF/font reproducibility insufficient. **Accepted.**

**v1.4 correction.** T-201 adds a `core+dev+pdf` CI profile (Ubuntu + Windows); pins OS-level WeasyPrint / Pango / Cairo dependencies in the Docker image + Windows CI (where the stack is available; otherwise marks Windows PDF tests as `semantic-identity-only` per v1.3 M3-05). Canonical fonts are **committed to the repo** under `fonts/` (via Git LFS for binary blobs); `tools/fonts/install_canonical_fonts.py` becomes a one-time bootstrap helper, not a `uv sync` hook. CI fails if `fonts/Noto-Sans-Regular.ttf` or `fonts/Noto-Mono-Regular.ttf` is absent.

### H4-10 — `AuditKeyProvider.current_key()` exposes raw HMAC bytes. **Accepted.**

**v1.4 correction.** Change `AuditKeyProvider` Protocol surface (T-312a):

```python
class AuditKeyProvider(Protocol):
    def mac(self, message: bytes) -> tuple[KeyVersionId, MacBytes]: ...
    def verify(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool: ...
    def verify_with_archived(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool: ...
    def rotate(self, reason: str, principal: AdminPrincipal | DeveloperBootstrapPrincipal) -> KeyVersionId: ...
    def current_key_version(self) -> KeyVersionId: ...
```

The raw `current_key() -> KeyMaterial` method is removed. Key bytes never leave the keystore adapter for production backends. The dev-only `file_keystore` may expose bytes for debugging but is configured via `config.audit_key_backend = "file_dev_unsafe"` (explicit unsafe naming) and refuses to start in non-dev modes. T-313b's broker uses `audit_key_provider.mac(message)` to compute HMAC chain entries; never sees the raw key.

## Moderate findings

### M4-01 — `SopTemplateLibrary` remains alongside new ports. **Accepted.**

**v1.4 correction.** Remove `SopTemplateLibrary` from port catalogue. The v1.3 port #5 slot is reassigned to `SopTemplateReadPort` (v1.3 port #25 → moves to canonical position #5 in v1.4). `YamlSopTemplateLoader` is removed from the composition root. The legacy YAML files remain in `catalogues/sop_templates/` as **bootstrap input** for T-316b's migration only; runtime reads go through `SqliteSopTemplateStoreRead`.

### M4-02 — Stale task IDs remain in active sections. **Accepted.**

**v1.4 correction.** Purge `T-309a` / `T-309b` / unsplit `T-312` from active content (§ 2, § 3, § 4.3, § 4.5, § 7.5, Appendix B, Appendix C). Allowed only in historical sections (§ 7.4b Round-5, § 7.4c Round-6, § 7.4d Round-7 audit summaries) and `ROADMAP.md` Appendix A. New CI gate `test_no_stale_task_ids_in_active_sections.py` enforces.

### M4-03 — Manifest claims unverifiable now. **Accepted.**

**v1.4 correction.** `TASK_BOARD.md` and Appendix C add an explicit note: "Counts marked **(planned-generated)** become **(manifest-derived)** once T-204 produces the initial `docs/task_manifest.yaml` + `docs/module_manifest.yaml` + `docs/port_manifest.yaml`." Until T-204 runs, counts are hand-maintained against this agenda's task list.

### M4-04 — Dual-control enforcement needs explicit tests. **Accepted.**

**v1.4 correction.** Add T-1302 dual-control adversarial UAT scenarios:

- `tests/uat/adversarial/dual_control_same_admin_rejected.py` — institution enables `dual_control_flags.require_two_admins_for_revocation = True`; the same `AdminPrincipal` tries to mint then revoke a profile → second action denied with `DualControlViolation`.
- `tests/uat/adversarial/dual_control_two_admins_accepted.py` — same fixture but two distinct admin principals → both actions accepted.
- `tests/uat/adversarial/dual_control_advisory_signoff_pair_required.py` — `dual_control_flags.advisory_acknowledgement_requires_pair = True`; single-admin acknowledgement blocks gate; pair acknowledgement passes.

### M4-05 — Admin-service IPC OS-level authorisation underspecified. **Accepted.**

**v1.4 correction.** Add to T-1103b acceptance:

- `test_windows_named_pipe_acl_restricts_to_admin_sid` — verify the pipe SD restricts access to the Administrators group SID + the service account SID; non-admin local user denied.
- `test_posix_socket_mode_0660_owned_by_cev_admin_group` — verify socket file mode + owner; non-`cev-admin` group member denied via OS layer (before the application sees the request).
- `test_service_account_separation` — admin-service runs under a dedicated service account (`cev-admin-svc` on Linux; service account on Windows); the engine process runs under a different account; cross-account filesystem access verified denied.
- Manual verification steps documented in `docs/deployment/admin_service.md`.

### M4-06 — `ReviewQueueStore` append-only-vs-update wording. **Accepted.**

**v1.4 correction.** Clarify T-315 model:

- `AuthorisationRequest` rows: append-only (immutable once written).
- `ReviewQueueItemDecision` rows: append-only (each decision is a new row referencing the request).
- `ReviewQueueItem.status`: **derived** from the latest decision row by a read model (`pending` if no decision row; `under_review` if assigned but no resolution; `approved` / `denied` / `expired` per the latest decision).
- Test: `test_review_queue_status_derived_from_decision_rows` confirms status is reconstructable from append-only rows alone (no status update column).

### M4-07 — Appendix B traceability T-803 still attributes SOP-template admin writes. **Accepted.**

**v1.4 correction.** Update Appendix B T-803 row: remove "SOP-template admin writes (v1.2 B2-04 extension)"; clarify T-803 consumes `SopTemplateReadPort` only.

### M4-08 — Markdown structural drift in T-201 numbering and lifecycle wording. **Accepted.**

**v1.4 correction.** Fix T-201 SOP numbering (current jumps from 4 to 6 — renumber to consecutive). Update CI lifecycle table footer note from "v1.2" to "v1.4". Run a markdown structural linter pass.

## Scientific soundness — three-role concurrence

`/scientific-advisor`: "B4-01 is the most consequential. If the physical heading order in Section 2 places SOP/export task headings before screening, any code generator or sub-agent walking the section in order will implement and test SOP/export against mocks before the screening pipeline exists. The fix is mechanical — physically move the Phase 10 section — but it has to happen. B4-04's audit concurrency redesign also matters scientifically: a legal audit chain that can deadlock or silently bypass under contention is not auditable in practice. The single-writer audit-service is the safest pattern."

`/architect`: "B4-02 / B4-03 / B4-08 are the same defect class — new infrastructure tasks scheduled after their consumers. v1.4 fixes this systematically by splitting each new task into a Protocol+fake (early) and adapter+production (late). The dependent task can satisfy acceptance against the fake; the production adapter lands later. B4-06's Section 3 regeneration is the wiring counterpart — if Section 3 is stale, the composition root encodes the wrong security boundary. B4-09's `DecisionRecordSigner` ownership is the last cryptographic-identity gap; v1.4 closes it via T-314."

`/dev-orchestrator`: "B4-07 is a docs-as-code reality check: the manifest authority was claimed but the authoring path was undefined. v1.4 makes `docs/module_manifest.yaml` manually-authored against the agenda; the generator is removed. M4-01 to M4-08 are docs-cleanup that we should have caught — v1.4 does the cleanup pass and adds CI gates so future drift is caught at PR time."

## Summary table

| Finding | Severity | Verdict | v1.4 change action |
|---|---|---|---|
| B4-01 | Blocking | Accepted | Physically reorder Section 2: Phase 10 inserted between 9a and 8b; `task_manifest_generator.py` uses explicit phase-order table; CI fixture asserts T-1001/T-1002 precede T-803/T-806b/T-903 |
| B4-02 | Blocking | Accepted | T-314 split: T-314a (Protocols+fakes, before T-310) + T-314b (production adapters + key lifecycle, after T-311) |
| B4-03 | Blocking | Accepted | T-313 split: T-313a (Protocols+fake brokers, before T-310) + T-313b (production audit-service broker, after T-311) |
| B4-04 | Blocking | Accepted | Single audit-service writer model; engine + admin processes append via IPC; T-313b owns audit-service implementation |
| B4-05 | Blocking | Accepted | T-316 split: T-316a (Phase 3, ports + value objects) + T-316b (Phase 4 after catalogue, signed SQLite store + bootstrap); `SopTemplateLibrary` + `YamlSopTemplateLoader` removed from composition root |
| B4-06 | Blocking | Accepted | § 3 regenerated end-to-end for v1.4; stale-task-ID CI check; composition root rewritten; persistence table single-writer audit-service |
| B4-07 | Blocking | Accepted | `docs/module_manifest.yaml` manually authored; `architecture_manifest_generator.py` removed; ARCHITECTURE.md treated as checked reference (informational consistency check) |
| B4-08 | Blocking | Accepted | T-1103 split: T-1103a (Protocol + IPC contract, before T-1101) + T-1103b (admin-service implementation + ACL/ReviewQueueAdminPort, after T-1101/T-1102); T-1101/T-1102 forbidden from importing AdminActionHandler |
| B4-09 | Blocking | Accepted | T-314 extended: T-314a adds DecisionRecordSigner Protocol + fakes; T-314b adds production per-principal signer + key lifecycle + offline verifier + compromised-key response |
| H4-01 | High | Accepted | `ReviewQueueAdminPort` added; admin-service constructor receives it; IPC verb `triage_review_queue_item`; user/API self-resolve test |
| H4-02 | High | Accepted | `no-self-authorisation-check` scope expanded to 6 surfaces; activation milestones split; three new gates `no-direct-admin-handler-import-check`, `audit-append-port-only-check`, `sop-template-admin-port-only-check` |
| H4-03 | High | Accepted | T-204 adds `tools/initial_task_brief_generator.py`; CI gate `test_task_brief_coverage.py` |
| H4-04 | High | Accepted | New **T-316c** (Phase 4) — production SOP-template signer + verifier + key lifecycle + offline verifier |
| H4-05 | High | Accepted | T-312b: indefinite audit-key archive retention via institutional escrow; in-process keystore retains current + recent only |
| H4-06 | High | Accepted | Agenda § 0.3 paragraph documenting `DeveloperPrincipal` → `DeveloperBootstrapPrincipal` interpretation in admin contexts; v1.6 source-doc amendment scheduled |
| H4-07 | High | Accepted | ROADMAP active sections regenerated; stale-token CI check |
| H4-08 | High | Accepted | Manifest-derived counts; `tools/task_count_reporter.py`; CI assertion |
| H4-09 | High | Accepted | `core+dev+pdf` CI profile; OS-level WeasyPrint deps pinned; canonical fonts committed via Git LFS (not network-downloaded) |
| H4-10 | High | Accepted | `AuditKeyProvider` Protocol changed: `mac(message)` / `verify(...)` / `rotate(...)` replace `current_key()`; raw key bytes never leave the keystore in production |
| M4-01 | Moderate | Accepted | `SopTemplateLibrary` removed from canonical port catalogue; legacy YAML files remain only as T-316b bootstrap input |
| M4-02 | Moderate | Accepted | Stale `T-309a` / `T-309b` / unsplit `T-312` purged from active content; CI gate `test_no_stale_task_ids_in_active_sections.py` |
| M4-03 | Moderate | Accepted | TASK_BOARD + Appendix C counts marked `(planned-generated)` until T-204 runs |
| M4-04 | Moderate | Accepted | T-1302 dual-control UAT: same-admin rejected, two-admins accepted, advisory-pair required |
| M4-05 | Moderate | Accepted | T-1103b adds Windows pipe ACL + POSIX socket mode + service-account separation tests + manual verification steps |
| M4-06 | Moderate | Accepted | T-315 model clarified: `AuthorisationRequest` + `ReviewQueueItemDecision` append-only; `status` derived from latest decision row |
| M4-07 | Moderate | Accepted | Appendix B T-803 row updated: SOP-template admin writes removed (owned by T-316b) |
| M4-08 | Moderate | Accepted | T-201 SOP numbering renumbered consecutively; lifecycle table footer updated to v1.4; markdown structural lint pass |

**Sign-off:** Three roles unanimously approve v1.4.

`/architect`: "Section 2 physical reorder + task splits (T-313 / T-314 / T-316 / T-1103) eliminate the build-order defects. Single-writer audit-service makes the audit chain executable. § 3 regenerated. Approved."

`/scientific-advisor`: "Screening physically precedes SOP / export in the build queue and in the manifest. Dual-control UAT scenarios are explicit. SOP-template signer + signature verifier + key lifecycle (T-316c) close the institutional integrity gap. Approved."

`/dev-orchestrator`: "Manifest authority is realistic (manually authored). Initial-brief generator unblocks the task-acceptance gate. Stale-token CI prevents drift recurrence. PDF/font reproducibility has a real CI profile. Approved."

---

*End of CODING_AGENDA_Fourth_Round_Audit_Response.md.*
