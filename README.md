# Cloning / Expression Vector Design — Project Root

**Established:** 2026-05-13
**Purpose:** foundation and working directory for a *universal cloning / expression vector design software* — the long-term goal is a program that takes a biological objective (host, cargo, expression level, biosafety tier) and produces a verified, software-validated, standards-serialised vector design ready to order.
**Status:** conceptual + knowledge foundations complete; software design and implementation begin from here.

---

## 1. What lives in this directory

| File | Role | Size |
|---|---|---|
| `Cloning_and_Expression_Vector_Design_Knowledge_Base_v1_0.md` | Original v1.0 conceptual primer (preserved as historical reference). | ~ 45 KB |
| `Cloning_KB_v2_Audit_Report.md` | Section-by-section cross-audit of v1.0 against the literature; explains exactly what changed in v2.0 and why. | ~ 17 KB |
| `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` | **Source-of-truth machine-actionable knowledge base** — parts catalogues with quantitative parameters, host/chassis tables, 25 parametric validation rules, decision logic, SBOL/GenBank/screening hook contracts, internal data schema sketch, full citation chain. | ~ 88 KB |
| `Cloning_Expression_Vector_Design_White_Paper.md` | **First-principles human-readable white paper** — pedagogical for first-time learners; 33 ASCII workflow diagrams; ~ 120-term glossary; covers bacterial, plant, and mammalian hosts; three worked examples. | ~ 119 KB |
| `REQUIREMENTS.md` | **Software Requirements Specification (SRS) — Draft v0.1.** Captures the 8 explicit user-stated requirements (UR-01 … UR-08) plus the full expansion into ~150 functional requirements, 54 molecular-genetics rules (MR), 30 wet-lab workflow rules (WR), 17 supplier/synthesis-vendor rules (SR), 10 biosafety/biosecurity rules (BR), non-functional requirements, architectural constraints, data-model requirements, acceptance criteria, MoSCoW × ROADMAP phase mapping, and 10 open questions for the architect. | ~ 73 KB |
| `ARCHITECTURE.md` | **Authoritative architectural blueprint — Finalised v1.5** (v1.0 → v1.1 Codex first audit → v1.2 sponsor sharpening of C1 → v1.3 sponsor role-hierarchy clarification → v1.4 Codex second audit + B3 sponsor defense → v1.5 sponsor strengthening of B3 mitigation — active, auditable, design-record-tied advisory acknowledgement, no passive UI warnings). Hexagonal modular-monolith architecture in Python with `domain.ports/` separation (B7); coordinate-and-graph data model with formal location algebra (M3) and structured `Qualifier` (B6); annotated `ImportedConstruct` / `AnnotatedConstruct` I/O contracts (B5); role-keyed `HostContext` and contextual `HostCompatibilityConstraints` (M5); `engine.sequence_analysis`; split `engine.protocol` into `engine.design_plan` (always renderable) + `engine.sop_protocol` (gated, post-screening, post-authorisation per v1.4 B2); new `engine.risk_classification` advisory layer (B3 mitigation) + `engine.vlp_policy` (M9); new `engine.controls` with mechanistic validation (N8); split `SecurityRole` vs `OperationalRole` (M6); admin-only `AuthorisationProfile` with expanded `CoveredBiologicalScope` (B4) + dual-control flags as opt-in (B3); split authorisation ports — Read / AdminWrite / Bootstrap (B8); signed `DecisionRecord` + `RoleSnapshot` (B9); `ScreeningProviderTrustPolicy` for institution-controlled adapter trust (B10); five typed hashes (M2); three separated event streams — design / governance / export (M12); expanded `DerivationEnvironment` covering profile/SOP/screening/plugin/LLM/policy/redaction hashes (B11); four typed safety gates; `domain.types.sop_protected` namespace prevents `DesignRealisationPlan` from carrying operational fields (M11); four export profiles with redaction policies (N6); BSL-4 hard block (M7); MS-* rule family; source-grade citation gate; per-catalogue maintenance metadata. CI gates: `no-self-authorisation-check`, `import-linter`, `sop-after-gates-check`, `llm-output-policy-check`, `audit-traceability-check`, `plugin-manifest-signature`, `stale-catalogue-check`, `source-grade-citation-check`, `no-domain-impurity-check`. 20-item residual risk register (R-17 LLM unsafe output, R-18 plugin trust escalation, R-19 export PII leak, R-20 unsupported BSL tier are new in v1.4). Produced by `/architect` + `/scientific-advisor` + `/dev-orchestrator` through 4 rounds of internal falsification + first Codex audit (31/31 accepted) + sponsor sharpening + sponsor role clarification + second Codex audit (**31/32 accepted, 1 defended with mitigation**). | ~ 140 KB |
| `audit report/ARCHITECTURE_Audit_Report.md` | **First external audit by Codex** (senior molecular-biology + senior software-architecture reviewer stance). 6 critical + 10 major + 15 moderate findings. | ~ 30 KB |
| `audit report/ARCHITECTURE_Audit_Response.md` | **First three-role audit response** with per-finding adjudication (31/31 accepted; 0 defended). The audit trail justifying every v1.1 / v1.2 / v1.3 change. | ~ 45 KB |
| `audit report/ARCHITECTURE_Second_Audit_Report_v1_2.md` | **Second external audit by Codex** on v1.3. 12 blocking + 13 major + 8 moderate findings. | ~ 30 KB |
| `audit report/ARCHITECTURE_Second_Audit_Response.md` | **Second three-role audit response** with per-finding adjudication (**31/32 accepted, 1 defended — B3 with advisory `BiosafetyClassificationLayer` mitigation per sponsor instruction**); plus the **v1.5 sponsor strengthening note** on B3 (active, auditable, design-record-tied advisory acknowledgement; no passive UI warnings; full approval trace logged). Includes the structured traceability table (M13). | ~ 50 KB |
| `ROADMAP.md` | **Derived from `ARCHITECTURE.md` v1.5.** 14-phase plan (Phase 0 + 1 + 2 complete; Phase 3 implementation is in progress). Each phase has owner / model tier / inputs / deliverables / six-dimension audit exit criteria. Stretch phases 14–18 listed but uncommitted. Regeneration policy on the last page. | ~ 45 KB |
| `CODING_AGENDA.md` | **Authoritative software development working plan — Finalised v1.5**. Fifth-round consistency release after `audit report/CODING_AGENDA_Fifth_Round_Audit_Report.md`: Phase 3 physical order fixed, stale legacy profile-signing card removed, Phase 3/4 counts set to 19/8, canonical port inventory corrected to 50, Section 3 wiring made executable, source docs aligned to `SopTemplateReadPort` / `SopTemplateAdminWritePort`, `DeveloperBootstrapPrincipal`, `interface.audit_service`, and `interface.admin_service`. | ~ 320 KB |
| `audit report/CODING_AGENDA_Fifth_Round_Audit_Response.md` | Fifth-round audit response: all 25 findings accepted, with resolution trace and verification command. | small |
| `TASK_BOARD.md` | **War-room dashboard companion to CODING_AGENDA.md.** Live status of every task (planned / in-progress / done / blocked); phase exit status against the six-dimension audit; risk register status with mitigation ownership; CI gate status. Updated by `/dev-orchestrator` on every task state transition; live mirror in Phase 11+ via `vector-design status` CLI. | ~ 15 KB |
| `README.md` | This file. | this directory |
| `docs/task_manifest.yaml` / `docs/port_manifest.yaml` / `docs/module_manifest.yaml` | Seed machine-readable manifests used by Codex and `tools/agenda_consistency_check.py` before T-204 implements production generators. | generated seed |
| `AGENTS.md` | Codex working instructions for future agents in this folder. | small |
| `tools/agenda_consistency_check.py` | Local consistency checker for active task counts/order/stale tokens/port totals/support-doc drift. | small |
| `MS2_CP_Vector_Design_Handover_Package_v1_0.zip` | **Pre-existing** MS2 coat-protein VLP vector-design handover package — project-specific archive referenced by v2.0 §17 and v1.0 §10 (MS2/phage/VLP notes). Unzip when working on MS2 / phage-display / VLP cargo-delivery designs. Not consumed by Phase 1 (system architecture); resurfaces during phage/VLP-template work. | ~ 18.4 MB |

## 2. How the four foundational documents relate

```
                  ┌───────────────────────────────────┐
                  │  v1.0  (historical primer)        │
                  └────────────────┬──────────────────┘
                                   │ audited and enriched
                                   ▼
   ┌─────────────────────┐   ┌────────────────────────────────┐
   │  Audit Report       │ ◄─┤  v2.0  (software-grade KB)     │
   │  (what changed)     │   │  — citations, parameters,      │
   └─────────────────────┘   │    schemas, validation rules   │
                             └────────────────┬───────────────┘
                                              │
                          (corresponds 1:1 to)│
                                              ▼
                             ┌────────────────────────────────┐
                             │  White Paper                   │
                             │  — first-principles narrative  │
                             │  — drives UI / help / onboard. │
                             └────────────────────────────────┘
```

When the v2.0 KB and the white paper appear to disagree, the citation chain in v2.0 is the source of truth and the white paper is updated to match.

## 3. Audience map — who reads what

| If you are… | Read first | Then |
|---|---|---|
| A first-time learner with no molecular-biology background | `Cloning_Expression_Vector_Design_White_Paper.md` Parts I–II | The rest of the white paper, then v2.0 §5 and §6 |
| A software architect designing the data model and rule engine | v2.0 §4, §8, §9, §15 | White paper Part V; v2.0 §14 (templates), §16 (failure modes) |
| A developer implementing assembly-method pickers | v2.0 §7 (assembly + overhang-fidelity datasets) and §11 (synthesis constraints) | White paper §13–17 |
| A biologist designing a real construct | White paper Part VI (worked examples) | v2.0 §14 (parameterised templates) |
| A regulatory / biosafety reviewer | v2.0 §12 (screening framework) and §13 (provenance/MTA) | White paper §23 |
| Auditing what the v2.0 KB added vs v1.0 | `Cloning_KB_v2_Audit_Report.md` | v2.0 §18 (source registry) |

## 4. Working conventions for this project

- **Source-of-truth hierarchy.** v2.0 KB > white paper > v1.0 primer. Every new code rule must trace to a citation in v2.0 §18.
- **No fabricated citations.** Any peer-reviewed claim must have a PMID, DOI, or PMC ID in v2.0 §18. Unverified items are explicitly flagged in v2.0 §19.
- **Standards-first.** Designs serialise to **SBOL 3** + **GenBank** + **FASTA**. Internal types map 1:1 to SBOL ComponentDefinition / Sequence / Range / Role.
- **Hard vs soft validation rules** (v2.0 §9). Hard rules block ordering; soft rules warn and require user acknowledgement.
- **Biosafety hook** (v2.0 §12). The software does not decide biosafety; it routes sequences to a configured adaptor (IGSC v3.0 / IBBIS Common Mechanism / SecureDNA / institutional) and records the verdict in construct metadata.
- **Provenance** (v2.0 §13). Every construct has a UUID, a SHA256 of its canonical-orientation sequence, a parent lineage, an MTA/licence tag, and an embedded SBOL record.
- **Codex working style.** Future agents should start with `AGENTS.md`, run `tools/agenda_consistency_check.py`, and use the seed manifests as the local machine-readable map before editing long-form plans.

## 5. Next milestones

Phase 2 scaffold, Phase 3, Phase 4, Phase 5, T-601a..k, T-602, T-603, and T-606 are complete locally. T-606 added `app.design_service` create/open/amend/compile/replay use cases over the event-sourced session engine plus explicit phase-local `Awaiting*` pending states for downstream services. Before opening T-607, run `python tools/agenda_consistency_check.py`, then use:

```powershell
python -m uv sync --frozen --no-editable --group dev --extra io
python -m uv run --no-editable python tools/ci/run_pytest.py -m "not slow"
```

See `ROADMAP.md` and `TASK_BOARD.md` for the prioritised phase plan. Short version: catalogues → validation engine → assembly/I/O → screening → gated SOP/export → CLI/API/UI.

## 6. Disclaimer

This project is a research/engineering effort. Outputs are advisory; no construct produced by software here may bypass the institutional biosafety committee, the chosen synthesis vendor's screening, or the user's professional judgement. See the disclaimer at the end of v2.0 §19.
