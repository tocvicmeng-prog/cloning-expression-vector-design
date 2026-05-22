# Fork-Readiness Operational Checklist

**Status:** NORMATIVE operational mirror of `ARCHITECTURE.md` § 9.6 (Fork-Readiness Memorandum).
**Owner:** future fork engineering team + counsel.
**Created:** 2026-05-23, task T-1411 (v0.2 Enrichment Amendment).
**Authority:** the binding source is `ARCHITECTURE.md` § 9.6. This checklist is its operational mirror — concrete verification commands and counsel-review certificate template.

This document is consulted when a future engineering team initiates a commercial fork of the project. Every item below MUST be verified, documented, and (where indicated) attached to the release manifest before any commercial-release tag is published.

---

## How to use this checklist

For each section below, the fork maintainer:

1. Verifies the item against the current state of the fork's codebase + corpus.
2. Records evidence (test output, file hashes, ToS snapshot URLs, counsel-review IDs) in the fork's release notes.
3. Where a verification script exists under `tools/fork_readiness/`, run it and attach the output.
4. On completion of all sections, complete the counsel-review certificate (§ 6) and attach to the release manifest.

**No commercial release tag is valid until every checklist item is verified and the counsel-review certificate is signed.**

---

## (a) Datasets — exclude or substitute

| # | Item | Verification |
|---|---|---|
| (a.1) | Records under `docs/ml_corpus/records/cc-by-sa/` are EXCLUDED from the commercial fork's training data. | Confirm `partition_default: sa_free` is locked in `corpus_manifest.yaml`. Run: `python -m tools.fork_readiness.verify_partition --release-tag X.Y.Z` (stub at v0.2 — see § 7). |
| (a.2) | Every record has `sequence_license.commercial_use_allowed: true` AND `annotation_license.commercial_use_allowed: true`. | Run: `python -m tools.fork_readiness.verify_license_completeness` (stub — see § 7). |
| (a.3) | No record carries `sequence_license.ml_training_allowed: false` (excluded entirely) or `annotation_license.ml_training_allowed: false` (annotation stripped, sequence retained). | Run: `python -m tools.fork_readiness.verify_ml_training_consent`. |
| (a.4) | No record has `provenance.source == addgene_metadata_only` (default-deny per FR-ML-04). | Schema-level check confirmed at landing of T-1402. Re-verify with `python -m tools.fork_readiness.verify_provenance_sources`. |
| (a.5) | All records added since the last counsel-reviewed corpus snapshot are quarantined until counsel-reviewed for the fork's commercial context. | Compare `corpus_manifest.yaml::records[].provenance.retrieved_at` against the last counsel-review certificate date. |

---

## (b) Workflows — relax or tighten

| # | Item | Verification |
|---|---|---|
| (b.1) | Default training partition is `partition: sa_free` ONLY — `partition: full` is unavailable in the commercial fork. | `tools/release/corpus_release_gate.py` (T-1409) enforces at release-tag time. |
| (b.2) | Release-gate's commercial criteria are enabled: 100% records with `commercial_use_allowed: true`, counsel-review certificate attached, cross-check coverage ≥ 95%. | Run: `python -m tools.release.corpus_release_gate --tag X.Y.Z --commercial`. |
| (b.3) | SnapGene cross-check coverage ≥ 95% (tighter than the 90% research threshold). | Reported in `corpus_manifest.yaml::license_aggregate.cross_check_coverage`. |
| (b.4) | ToS re-check has been run immediately on fork-creation, then continues quarterly with commercial-lens questions added. | Archive under `docs/ip_policy/tos_snapshots/{YYYY-QQ}/`. |
| (b.5) | Counsel review precedes every commercial release. | Certificate template at § 6 of this document. |
| (b.6) | Vendor license outreach (deferred IPQ-3) is complete before commercial release. | Document outreach status per vendor in the release notes. |

---

## (c) Design elements — re-point

| # | Item | Verification |
|---|---|---|
| (c.1) | `corpus_manifest.yaml::partition_default` is `sa_free`. `partition: full` is removed from the commercial fork's manifest entirely. | Manual inspection + `grep -c 'partition: full' docs/ml_corpus/corpus_manifest.yaml` → 0. |
| (c.2) | Trained-model checkpoints from `partition: full` are NOT distributed in the commercial fork. Only `partition: sa_free`-trained checkpoints survive. | Inspect training manifests; reject any checkpoint not declaring `partition: sa_free`. |
| (c.3) | Training manifests declare `partition`, `counsel_review_passed: true`, and `counsel_review_date`. | Schema-validate the training manifests. |
| (c.4) | Trademark / branding is distinct from "Cloning Expression Vector Design Toolkit". | Counsel review + name search. |
| (c.5) | Repo-root `IP_POLICY.md` is replaced with a commercial-edition policy referencing this memorandum. | Manual diff against the research-edition `IP_POLICY.md`. |

---

## (d) License + IP posture for the fork

| # | Item | Verification |
|---|---|---|
| (d.1) | Toolkit code on the fork is GPL-3.0 (inherited as-is). | `LICENSE` file SHA-256 unchanged from upstream. |
| (d.2) | Trained-model weights are released under Apache-2.0 / MIT / proprietary — NOT CC-BY-SA, NOT GPL. | Inspect model-weights distribution metadata. |
| (d.3) | Aggregate attribution is preserved via `LICENSES/THIRD_PARTY_NOTICES.md` (every CC-BY record's attribution captured). | Generate fresh attributions file at release time: `python -m tools.fork_readiness.regenerate_attributions`. |
| (d.4) | SnapGene nominative-use disclaimer present and current per IP-auditor § 3.4. | Inspect `LICENSES/THIRD_PARTY_NOTICES.md` § 1. |
| (d.5) | All vendor ToS pages re-verified at fork-creation and at every commercial release; archived under `docs/ip_policy/tos_snapshots/`. | Verify timestamped perma.cc snapshots. |
| (d.6) | Counsel-review certificate attached to the release manifest. | See § 6 of this document. |

---

## (e) Regulatory posture for commercial release

| # | Item | Verification |
|---|---|---|
| (e.1) | Biosafety floor (MS-01..MS-06) re-evaluated for commercial deployment. | Engage `/scientific-advisor` + `/ip-auditor` joint review. |
| (e.2) | US Export Administration Regulations (EAR) — biotechnology software classification (ECCN 1E001 or related) verified. | US export counsel sign-off. |
| (e.3) | NIH DURC review status — commercial use at scale may attract NIH OSP DURC review. | Engage NIH Office of Science Policy if US-based commercial release. |
| (e.4) | Australian biosecurity legislation — Defence Trade Controls Act 2012 review for commercial distribution from GMExpression. | AU counsel sign-off. |
| (e.5) | EU AI Act — GPAI requirements (transparency, training-data summaries, copyright respect) apply if commercial scope is global. | EU counsel sign-off (out of project's stated jurisdictions; flag only if global scope). |
| (e.6) | Quarterly re-check of all regulatory items, same cadence as ToS re-check. | Schedule entry in `docs/ip_policy/tos_snapshots/{YYYY-QQ}/regulatory_review.md`. |

---

## 6. Counsel-review certificate template

A copy of this template is also at `tools/fork_readiness/counsel_review_certificate_template.md` for inclusion in the release manifest.

```yaml
counsel_review_certificate:
  release_tag: "X.Y.Z"
  fork_repository_url: "<url>"
  certificate_issued: "<ISO 8601 date>"
  certificate_expires: "<ISO 8601 date>"

  reviewers:
    - jurisdiction: "Australia"
      counsel_name: "<name>"
      counsel_firm: "<firm>"
      registration_id: "<AU registered patent/IP attorney number>"
      review_scope: "GPL-3.0 compatibility; AU Defence Trade Controls Act 2012; AU Trade Marks Act 1995 s122 nominative use; INSDC + iGEM + vendor ToS posture; biosecurity DSGT review."
    - jurisdiction: "United States (California)"
      counsel_name: "<name>"
      counsel_firm: "<firm>"
      bar_id: "<California bar number>"
      review_scope: "US Copyright Act 17 USC §107 (fair use) basis for any retained content; ML-training-data caselaw posture; US EAR ECCN 1E001 classification; NIH DURC determination if applicable; US Trademark Act nominative-use disclaimer review."

  verifications:
    section_a_datasets: { all_items_passed: true, evidence_file: "<path>" }
    section_b_workflows: { all_items_passed: true, evidence_file: "<path>" }
    section_c_design_elements: { all_items_passed: true, evidence_file: "<path>" }
    section_d_license_ip: { all_items_passed: true, evidence_file: "<path>" }
    section_e_regulatory: { all_items_passed: true, evidence_file: "<path>" }

  signature:
    method: "<wet ink / qualified e-signature / etc.>"
    timestamp: "<ISO 8601>"
    certificate_hash: "<sha256 of full certificate>"

  notes: |
    <Any additional caveats, conditional approvals, follow-up obligations.>
```

---

## 7. Verification script stubs (T-1411 deliverables)

The following script stubs are committed at T-1411 close. **They are not implemented at v0.2** — they exist as documented entry points for the future fork engineering team. Each stub records its NORMATIVE contract and expected output format.

| Script | Stub status | Contract |
|---|---|---|
| `tools/fork_readiness/verify_partition.py` | Stub | Walks corpus, asserts no `cc-by-sa/` records reachable from the active partition; asserts `corpus_manifest.yaml::partition_default == "sa_free"`. |
| `tools/fork_readiness/verify_license_completeness.py` | Stub | Walks corpus, asserts every record has `sequence_license.commercial_use_allowed: true` AND `annotation_license.commercial_use_allowed: true`. |
| `tools/fork_readiness/verify_ml_training_consent.py` | Stub | Walks corpus, asserts every record has `ml_training_allowed: true` on both license blocks; flags any record where annotation_license blocks ML training but sequence_license allows (annotation should be stripped). |
| `tools/fork_readiness/verify_provenance_sources.py` | Stub | Walks corpus, asserts no record carries `provenance.source: addgene_metadata_only`. |
| `tools/fork_readiness/regenerate_attributions.py` | Stub | Walks corpus, regenerates `LICENSES/THIRD_PARTY_NOTICES.md` aggregate attributions block from per-record `license.*.attribution_text`. |
| `tools/fork_readiness/counsel_review_certificate_template.md` | Template (this file's § 6 mirrored) | Counsel-review certificate template for inclusion in release manifests. |

Implementation of these scripts is the natural next step on fork creation; v0.2 ships only the documented contracts so the operational structure is in place.

---

## 8. Cross-references

- **`ARCHITECTURE.md` § 9.6** — NORMATIVE Fork-Readiness Memorandum (binding authority).
- **`IP_POLICY.md`** — counsel-facing policy (repo root).
- **`LICENSES/THIRD_PARTY_NOTICES.md`** — canonical trademark + attribution disclaimers.
- **`REQUIREMENTS.md` § 11.7** — BR-15 (ML license enforcement), BR-16 (SnapGene posture), BR-17 (CC-BY-SA partition).
- **`docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md`** § 6 — CC-BY-SA contagion analysis (basis for the partition strategy).
- **`docs/handover/2026-05-23_host_marker_ml_corpus_development_plan.md`** § 10 — joint-plan fork-readiness scope.

---

> **Disclaimer:** This checklist is a counsel-facing internal artefact. It is not legal advice. The binding determinations on every regulatory and IP item belong to qualified IP counsel in the relevant jurisdiction (AU registered patent / IP attorney + California-licensed counsel with copyright + AI-data-rights practice). All commercial-release decisions require a current counsel-review certificate per § 6.
