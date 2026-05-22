# Architect Analysis — Host / Marker / ML-Corpus Enrichment

**Project:** Cloning & Expression Vector Design Toolkit (post-`v0.1.0`)
**Document type:** Architect analysis (cadence step 3) — schema + port + CI-gate design
**Author:** `/architect`
**Date:** 2026-05-23
**Upstream brief:** `docs/handover/2026-05-23_host_marker_ml_corpus_initial_report.md` (accepted by user).
**Parallel work:** `/ip-auditor` runs cadence step 4 on briefing § 4 of the same initial report.
**Status:** **DRAFT — pending user acceptance.** No `ARCHITECTURE.md`, `CODING_AGENDA.md`, `REQUIREMENTS.md`, `TASK_BOARD.md`, `schemas/*`, `catalogues/*`, or `src/*` changes have been made in this turn. Per the project's 10-step standing cadence ([[cev-workflow-discipline]]), all of those are downstream of this analysis.

---

## 0. Working principle reference

This analysis is produced under the project's standing 10-step cadence:

1. `/scientific-advisor` → initial report ✅
2. User accepts the report ✅
3. **`/architect` → architecture analysis (this document)**
4. `/ip-auditor` → IP/ToS analysis (parallel, separate document)
5. User accepts both analyses
6. `REQUIREMENTS.md` updated
7. `/scientific-advisor` + `/dev-orchestrator` + `/architect` jointly draft the development plan
8. `ARCHITECTURE.md` updated
9. `CODING_AGENDA.md` updated
10. `TASK_BOARD.md` updated → implementation begins

The deliverable here is a **design proposal**, not a binding architecture change. The binding changes happen at step 8.

---

## 1. Scope inherited from initial report (confirmed)

| Track | Deliverable |
|---|---|
| A | Extend `catalogues/hosts.yaml` to cover ~30 named strains (15 *E. coli*, 6 *K. phaffii*, 5 *S. cerevisiae*). |
| B | New `catalogues/markers.yaml` + `schemas/markers.schema.json` v1.0. Deprecate the `markers:` block currently in `parts.yaml`. |
| C | New `docs/ml_corpus/` subsystem with its own folder layout, schemas, license matrix, and SnapGene cross-check log. |

Decisions locked in by user (carried into this analysis verbatim):

1. Markers catalogue is **split** into its own file + schema.
2. *Pichia pastoris* → **`Komagataella phaffii`** canonical, `Pichia pastoris` as alias.
3. ML corpus location: **sibling folder `docs/ml_corpus/`** inside the repo.
4. SnapGene posture: **index-only**, with manual cross-check of ingested sequences against the SnapGene reference record. No automated scraping.
5. Antibiotic working-concentration reference: **Sambrook 4th ed. Appendix A1** canonical.

---

## 2. Schema deltas

### 2.1 `schemas/hosts.schema.json` v1.0 → v1.1

#### 2.1.1 Design principle: additive, backward-compatible

All ten new field families are **optional** in v1.1. Existing host records in `catalogues/hosts.yaml` (DH5α, TOP10, JM109, XL1-Blue, Stbl3, BL21 baseline, cell-free hosts, yeast hosts, mammalian hosts, insect hosts, plant hosts, phage/VLP hosts) remain valid under v1.1 without modification. New strain records use the new fields; legacy records are enriched opportunistically in a follow-up backfill task (see § 6 Q4).

This avoids the failure mode of a `required:` bump that invalidates 50+ existing entries the day v1.1 lands.

#### 2.1.2 Concrete JSONSchema fragments to add under `items.properties`

```json
{
  "aliases": {
    "type": "array",
    "items": {"type": "string", "minLength": 1},
    "description": "Alternate species/genus names. Example for K. phaffii: ['Pichia pastoris']. Resolver must match aliases case-insensitively."
  },
  "t7_lysogen": {
    "type": ["boolean", "null"],
    "description": "True for (DE3) lysogens carrying T7 RNA polymerase under lacUV5. Null for hosts where T7 lysogeny is N/A (yeasts, cell-free)."
  },
  "protease_status": {
    "type": "object",
    "properties": {
      "lon": {"type": "string", "enum": ["present", "deleted", "null"]},
      "ompT": {"type": "string", "enum": ["present", "deleted", "null"]}
    },
    "additionalProperties": false,
    "description": "lon (cytoplasmic ATP-dependent) and ompT (outer-membrane) protease phenotypes. BL21 lineage is lon-/ompT-; K12 lineage is lon+/ompT+."
  },
  "disulfide_environment": {
    "type": "object",
    "properties": {
      "cytoplasm_state": {"type": "string", "enum": ["reducing_default", "oxidising", "shuffle_engineered", "null"]},
      "trxB_status": {"type": "string", "enum": ["wt", "deleted", "null"]},
      "gor_status": {"type": "string", "enum": ["wt", "deleted", "null"]}
    },
    "additionalProperties": false,
    "description": "Cytoplasmic redox phenotype. Origami: trxB-/gor- oxidising. SHuffle: trxB-/gor-/DsbC+. Default E. coli: reducing."
  },
  "rare_codon_supplementation": {
    "type": "array",
    "items": {"type": "string", "minLength": 1},
    "description": "List of supplied rare-codon tRNA genes or the plasmid that carries them. Example for Rosetta: ['pRARE:argU,argW,ileX,glyT,leuW,proL']."
  },
  "plasmid_addons": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["id", "function", "antibiotic"],
      "properties": {
        "id": {"type": "string", "minLength": 1},
        "function": {"type": "string", "minLength": 1},
        "antibiotic": {"type": "string", "minLength": 1},
        "notes": {"type": "string"}
      },
      "additionalProperties": false
    },
    "description": "Plasmid-borne host add-ons. Examples: pLysS (T7 lysozyme low, Cm), pLysE (T7 lysozyme high, Cm), pRARE (rare-codon tRNAs, Cm), pRARE2, pLacIQ (extra lacI, Cm/Spec)."
  },
  "t7_lysozyme_load": {
    "type": "string",
    "enum": ["none", "pLysS_low", "pLysE_high", "null"],
    "description": "Encoded T7 lysozyme load (a derived field from plasmid_addons but kept first-class for rule-engine convenience). None for non-T7-system hosts."
  },
  "recombination_phenotype": {
    "type": "object",
    "properties": {
      "recA": {"type": "string", "enum": ["wt", "deleted", "null"]},
      "endA": {"type": "string", "enum": ["wt", "deleted", "null"]},
      "recBCD_status": {"type": "string", "enum": ["wt", "deleted", "modified", "null"]}
    },
    "additionalProperties": false,
    "description": "Homologous-recombination and exonuclease phenotype. recA- endA- = stable propagation; recBCD-modified strains (Stbl2, Stbl3, Stbl4, JC8679) support direct repeats / lentiviral LTRs."
  },
  "methylation_phenotype": {
    "type": "object",
    "properties": {
      "dam": {"type": "string", "enum": ["wt", "deleted", "null"]},
      "dcm": {"type": "string", "enum": ["wt", "deleted", "null"]},
      "hsdRMS": {"type": "string", "enum": ["wt", "deleted", "K12_pattern", "B_pattern", "null"]}
    },
    "additionalProperties": false,
    "description": "DNA-methylation phenotype. Affects which restriction enzymes can cut plasmid prep (e.g., DpnI vs DpnII vs MboI; XbaI/NheI blocked by dam; PstI blocked by dcm)."
  },
  "recommended_selection_markers": {
    "type": "array",
    "items": {"type": "string", "minLength": 1, "pattern": "^marker\\.[a-z0-9_]+$"},
    "description": "Cross-link to markers catalogue. Each entry must resolve to an existing marker id in catalogues/markers.yaml (enforced by host-marker-link-integrity-check CI gate)."
  },
  "vendor_strain_refs": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["vendor", "catalogue_id", "accessed"],
      "properties": {
        "vendor": {"type": "string", "minLength": 1},
        "catalogue_id": {"type": "string", "minLength": 1},
        "url": {"type": "string"},
        "accessed": {"type": "string", "format": "date"}
      },
      "additionalProperties": false
    },
    "description": "Vendor SKU references for the strain. Example for BL21(DE3): [{vendor: 'NEB', catalogue_id: 'C2527H', accessed: '2026-05-23'}, {vendor: 'Sigma-Aldrich', catalogue_id: 'CMC0014', accessed: '2026-05-23'}]."
  }
}
```

#### 2.1.3 `schema_version` bump

`catalogues/hosts.yaml` top-level `schema_version: "1.0.0"` → `"1.1.0"`.

The `agenda_consistency_check.py` extension (§ 4.4) verifies this bump is present whenever any of the v1.1 fields appear.

### 2.2 `schemas/markers.schema.json` v1.0 (new file)

#### 2.2.1 Top-level envelope (same pattern as hosts/parts/enzymes)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CEV selection-markers catalogue",
  "type": "object",
  "required": ["catalogue_id", "schema_version", "maintenance", "items"],
  "properties": {
    "catalogue_id": {"type": "string", "const": "cev.markers"},
    "schema_version": {"type": "string", "minLength": 1},
    "maintenance": {"$ref": "#/$defs/maintenance"},
    "citation_presets": {"type": "object"},
    "items": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/marker"}}
  }
}
```

#### 2.2.2 Per-marker item

```json
{
  "$defs": {
    "marker": {
      "type": "object",
      "required": [
        "id",
        "name",
        "class",
        "gene",
        "mechanism",
        "plasmid_borne",
        "chromosomal",
        "working_concentrations",
        "incompatibilities",
        "use_cases",
        "citation",
        "maintenance"
      ],
      "properties": {
        "id": {"type": "string", "pattern": "^marker\\.[a-z0-9_]+$"},
        "name": {"type": "string", "minLength": 1},
        "class": {
          "type": "string",
          "enum": [
            "bacterial_antibiotic",
            "yeast_auxotrophic",
            "yeast_dominant",
            "mammalian_antibiotic",
            "counterselection"
          ]
        },
        "gene": {"type": "string", "minLength": 1},
        "mechanism": {"type": "string", "minLength": 1},
        "plasmid_borne": {"type": "boolean"},
        "chromosomal": {"type": "boolean"},
        "working_concentrations": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["host_class", "agent", "concentration_ugml", "medium", "citation"],
            "properties": {
              "host_class": {
                "type": "string",
                "enum": ["ecoli", "scerevisiae", "kphaffii", "mammalian", "insect", "plant"]
              },
              "agent": {"type": "string", "minLength": 1},
              "concentration_ugml": {
                "type": "object",
                "required": ["min", "typical", "max"],
                "properties": {
                  "min": {"type": "number", "exclusiveMinimum": 0},
                  "typical": {"type": "number", "exclusiveMinimum": 0},
                  "max": {"type": "number", "exclusiveMinimum": 0}
                }
              },
              "medium": {"type": "string", "minLength": 1},
              "carbon_source_qualifier": {"type": "string"},
              "notes": {"type": "string"},
              "citation": {"$ref": "#/$defs/citation"}
            }
          }
        },
        "counter_selection": {
          "type": ["object", "null"],
          "required": ["agent", "selection_medium", "citation"],
          "properties": {
            "agent": {"type": "string", "minLength": 1},
            "selection_medium": {"type": "string", "minLength": 1},
            "notes": {"type": "string"},
            "citation": {"$ref": "#/$defs/citation"}
          }
        },
        "host_genotype_requirement": {
          "type": "string",
          "description": "For auxotrophic markers, the required host genotype (e.g., 'ura3-Δ', 'leu2-Δ0'). For dominant markers, null/absent."
        },
        "incompatibilities": {
          "type": "array",
          "items": {"type": "string"}
        },
        "use_cases": {
          "type": "array",
          "minItems": 1,
          "items": {"type": "string"},
          "description": "Vector lineages / contexts where the marker is conventional. Example: ['pUC', 'pBR322', 'pET', 'pBAD']."
        },
        "citation": {"$ref": "#/$defs/citation"},
        "maintenance": {"$ref": "#/$defs/maintenance"}
      }
    },
    "citation": {
      "type": "object",
      "required": ["text", "grade", "accessed"],
      "properties": {
        "text": {"type": "string", "minLength": 1},
        "grade": {"type": "string", "enum": ["A1", "A2", "A3", "B1", "B2", "C"]},
        "accessed": {"type": "string", "format": "date"},
        "pmid": {"type": "string"},
        "doi": {"type": "string"},
        "url": {"type": "string"},
        "source_registry_ids": {"type": "array", "items": {"type": "string"}}
      }
    },
    "maintenance": {
      "type": "object",
      "required": ["retrieved_at", "valid_until", "source_url", "review_required_after"],
      "properties": {
        "retrieved_at": {"type": "string", "format": "date"},
        "valid_until": {"type": "string", "format": "date"},
        "source_url": {"type": "string", "minLength": 1},
        "review_required_after": {"type": "string", "format": "date"}
      }
    }
  }
}
```

**Note** on `working_concentrations` for auxotrophic markers: they have no μg/mL concentration. The schema currently requires `minItems: 1` for `working_concentrations`. Resolution: auxotrophic markers carry **one** entry per relevant host with a sentinel `concentration_ugml: {min: 0, typical: 0, max: 0}` and a `notes:` field reading "auxotrophic — selection on dropout medium, not concentration-based"; the `medium` field carries the dropout-medium identity (e.g., "SD -Ura (CSM-Ura)"). This keeps the schema uniform without splitting auxotrophic into a different shape. Validator note: a separate CI check (§ 4.1) warns if `class: yeast_auxotrophic` is combined with non-zero concentrations.

### 2.3 `docs/ml_corpus/schemas/corpus_record.schema.json` v1.0 (new file)

Lives **outside** `schemas/` deliberately, to make the runtime/training-data boundary visible in the file tree.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CEV ML training corpus record",
  "type": "object",
  "required": [
    "id",
    "category",
    "sequence",
    "annotation",
    "provenance",
    "license",
    "snapgene_crosscheck",
    "host_topology",
    "intended_use_category",
    "checksum"
  ],
  "properties": {
    "id": {"type": "string", "pattern": "^corpus\\.[a-z0-9_.-]+$"},
    "category": {
      "type": "string",
      "enum": [
        "backbone",
        "promoter",
        "terminator",
        "rbs",
        "kozak",
        "polyA",
        "ires",
        "2a_peptide",
        "mcs",
        "tag",
        "fluorescent_protein",
        "selection_cassette",
        "insulator",
        "wpre",
        "intron"
      ]
    },
    "sequence": {
      "type": "object",
      "required": ["bases", "topology", "length_bp"],
      "properties": {
        "bases": {"type": "string", "pattern": "^[ACGTacgtNn]+$"},
        "topology": {"type": "string", "enum": ["circular", "linear"]},
        "length_bp": {"type": "integer", "exclusiveMinimum": 0}
      }
    },
    "annotation": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "start", "end", "strand"],
        "properties": {
          "type": {"type": "string"},
          "start": {"type": "integer", "minimum": 0},
          "end": {"type": "integer", "exclusiveMinimum": 0},
          "strand": {"type": "string", "enum": ["+", "-", "."]},
          "qualifiers": {"type": "object"}
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["source", "retrieved_at", "retrieved_by"],
      "properties": {
        "source": {
          "type": "string",
          "enum": [
            "ncbi_genbank",
            "ebi_ena",
            "ddbj",
            "igem_registry",
            "jbei_ice",
            "dnasu",
            "addgene_metadata_only",
            "vendor_published_map",
            "primary_literature",
            "fpbase"
          ]
        },
        "accession_or_url": {"type": "string", "minLength": 1},
        "retrieved_at": {"type": "string", "format": "date-time"},
        "retrieved_by": {"type": "string", "minLength": 1}
      }
    },
    "license": {
      "type": "object",
      "required": [
        "spdx_id",
        "redistribution_allowed",
        "ml_training_allowed",
        "attribution_required",
        "source_text_url"
      ],
      "properties": {
        "spdx_id": {"type": "string", "minLength": 1},
        "redistribution_allowed": {"type": "boolean"},
        "ml_training_allowed": {"type": "boolean"},
        "attribution_required": {"type": "boolean"},
        "attribution_text": {"type": "string"},
        "source_text_url": {"type": "string", "minLength": 1},
        "notes": {"type": "string"}
      }
    },
    "snapgene_crosscheck": {
      "type": "object",
      "required": ["checked"],
      "properties": {
        "checked": {"type": "boolean"},
        "checked_at": {"type": "string", "format": "date-time"},
        "checker": {"type": "string"},
        "snapgene_record_name": {"type": "string"},
        "snapgene_record_url": {"type": "string"},
        "match": {"type": "boolean"},
        "discrepancy_resolution": {"type": "string"}
      },
      "allOf": [
        {
          "if": {"properties": {"checked": {"const": true}}},
          "then": {"required": ["checked_at", "checker", "snapgene_record_name", "match"]}
        }
      ]
    },
    "host_topology": {
      "type": "object",
      "required": ["host_class"],
      "properties": {
        "host_class": {"type": "string"},
        "replicon": {"type": "string"},
        "copy_number_class": {"type": "string", "enum": ["high", "medium", "low", "single", "null"]}
      }
    },
    "intended_use_category": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string"}
    },
    "checksum": {
      "type": "object",
      "required": ["algorithm", "value"],
      "properties": {
        "algorithm": {"type": "string", "enum": ["sha256", "sha512"]},
        "value": {"type": "string", "minLength": 1}
      }
    }
  }
}
```

**Decision on the cross-check field**: `snapgene_crosscheck.checked: false` is permitted (this is critical — see § 5.2). The `ml-corpus-license-check` CI gate emits a **warning**, not a hard fail, when a record has `checked: false`. The aggregate `corpus_manifest.yaml` reports the fraction of records that have been cross-checked, giving the user a tunable QC dial.

### 2.4 Migration guidance for existing records

| Catalogue file | Action |
|---|---|
| `catalogues/hosts.yaml` | (a) Bump `schema_version` to `"1.1.0"`. (b) Existing records remain valid with no field changes (all v1.1 fields are optional). (c) A follow-up backfill task (deferred to CODING_AGENDA) enriches DH5α, TOP10, JM109, XL1-Blue, Stbl3, and the BL21 baseline with the new fields where applicable. (d) The 30 new strains all carry the new fields. |
| `catalogues/parts.yaml` | (a) The `markers:` citation preset and any parts items with `role: marker` are deprecated. (b) Add a transitional `deprecated_in: "1.1.0"` flag to each affected entry. (c) Add a comment block at the top of the affected section pointing readers to `catalogues/markers.yaml`. (d) See § 3.3 below for the runtime migration. |
| `schemas/parts.schema.json` | No structural changes for v1.1. The schema continues to validate `role: marker` entries until the dual-read window closes (see § 3.3). |
| New file: `catalogues/markers.yaml` | Populated from scratch in step 10 by `/scientific-advisor` per the markers schema above. |
| New file: `schemas/markers.schema.json` v1.0 | Added per § 2.2. |
| New folder: `docs/ml_corpus/` | Created in step 10 with the layout in § 5.1. |

---

## 3. Composition root + ports

### 3.1 New `MarkersCataloguePort`

#### 3.1.1 Slot in port inventory

`docs/port_manifest.yaml` currently lists **50 canonical ports** (CODING_AGENDA v1.5 seed; the speculative six biological catalogue ports referenced in stale memory never landed). The new port slots in as:

```yaml
- port_id: 51
  port_name: "MarkersCataloguePort"
  category: "catalogue"
  owning_task: "TBD-by-dev-orchestrator-step-9"
  architecture_section: "4.5"
```

The `canonical_port_count` field bumps from 50 to 51. A new CI check (§ 4.4) enforces the port-manifest ↔ ARCHITECTURE.md count match.

#### 3.1.2 Protocol surface (proposed)

In `src/domain/ports/markers_catalogue.py` (path follows the existing `domain.ports.*` convention):

```python
from typing import Protocol, Sequence
from domain.types.markers import Marker, MarkerId, MarkerClass, HostClass


class MarkersCataloguePort(Protocol):
    """Read-only port over the markers catalogue.

    No write methods. Markers catalogue is rebuilt offline by /scientific-advisor
    + /rd-researcher; runtime only reads.
    """

    def get_by_id(self, marker_id: MarkerId) -> Marker: ...

    def list_all(self) -> Sequence[Marker]: ...

    def list_by_class(self, marker_class: MarkerClass) -> Sequence[Marker]: ...

    def list_compatible_with_host(self, host_id: str) -> Sequence[Marker]:
        """Returns markers whose working_concentrations list contains the host's
        chassis_class OR whose host_genotype_requirement is satisfied by the
        host's recombination_phenotype / methylation_phenotype.
        """

    def working_concentration(
        self, marker_id: MarkerId, host_class: HostClass, agent: str | None = None
    ) -> "WorkingConcentration | None":
        """Returns concentration_ugml block for the given (marker, host_class, agent).
        agent=None returns the canonical agent for that marker on that host_class.
        """
```

The corresponding adapter `src/adapter/catalogue/yaml_markers_catalogue.py` loads `catalogues/markers.yaml`, validates against `schemas/markers.schema.json`, and constructs the immutable in-memory model.

#### 3.1.3 Domain types (new module)

`src/domain/types/markers.py`:

```python
@dataclass(frozen=True)
class MarkerId:
    value: str  # validated against ^marker\.[a-z0-9_]+$

class MarkerClass(Enum):
    BACTERIAL_ANTIBIOTIC = "bacterial_antibiotic"
    YEAST_AUXOTROPHIC = "yeast_auxotrophic"
    YEAST_DOMINANT = "yeast_dominant"
    MAMMALIAN_ANTIBIOTIC = "mammalian_antibiotic"
    COUNTERSELECTION = "counterselection"

class HostClass(Enum):
    ECOLI = "ecoli"
    SCEREVISIAE = "scerevisiae"
    KPHAFFII = "kphaffii"
    MAMMALIAN = "mammalian"
    INSECT = "insect"
    PLANT = "plant"

@dataclass(frozen=True)
class WorkingConcentration:
    host_class: HostClass
    agent: str
    min_ugml: float
    typical_ugml: float
    max_ugml: float
    medium: str
    carbon_source_qualifier: str | None
    citation: Citation

@dataclass(frozen=True)
class CounterSelection:
    agent: str
    selection_medium: str
    notes: str | None
    citation: Citation

@dataclass(frozen=True)
class Marker:
    id: MarkerId
    name: str
    marker_class: MarkerClass
    gene: str
    mechanism: str
    plasmid_borne: bool
    chromosomal: bool
    working_concentrations: tuple[WorkingConcentration, ...]
    counter_selection: CounterSelection | None
    host_genotype_requirement: str | None
    incompatibilities: tuple[str, ...]
    use_cases: tuple[str, ...]
    citation: Citation
    maintenance: Maintenance
```

### 3.2 Engine updates

| Engine | Required change |
|---|---|
| `engine.compatibility` | Add a `MarkersCataloguePort` dependency. New rule resolver: when a host rule references `recommended_selection_markers[]`, resolve each entry via `markers.get_by_id()`. Add cross-check: marker's `working_concentrations[].host_class` must include the host's `chassis_class`, otherwise emit a `MR-MARKER-MISMATCH` advisory. |
| `engine.validation` | Add `MarkersCataloguePort` dependency to the validator construction. Any existing rule predicate that currently looks up a marker via `parts.yaml::markers` (probably MR-* rules touching antibiotic selection) is re-pointed to the new port during the dual-read window (§ 3.3). |
| `engine.risk_classification` | No change. Risk advisories are independent of marker source. |
| `engine.sequence_analysis` | No change. |
| `engine.vlp_policy` | No change. |
| `engine.screening_floor` (Phase 10 T-1002a, if landed) | No change — biosecurity floor is unrelated. |
| Composition root (`src/app/composition_root.py` or equivalent) | Wire `YamlMarkersCatalogue` instance into the engine-side container. Inject into `engine.compatibility` and `engine.validation` factories. |
| Admin service | No change (markers catalogue is read-only at runtime, edited offline). |

### 3.3 `parts.yaml::markers` deprecation — recommended migration strategy

**Recommendation: Dual-read window of one release cycle.** Hard cut-over is rejected because v0.1.0 rule predicates already depend on `parts.yaml::markers` and a single-PR switch risks breaking validation logic that has already gone through 8 audits.

| Phase | Behaviour | Duration |
|---|---|---|
| **A. Dual-read** | `MarkersCataloguePort` is implemented and populated. The validator and compatibility engine first try `MarkersCataloguePort.get_by_id()`; on miss, they fall back to a thin shim over `parts.yaml::markers`. A WARN-level log line records every fallback hit (visible in the governance event stream). | First release cycle after schema landing. ETA: ~1–2 weeks of implementation + 1 release cycle of observation. |
| **B. New-port-only** | The shim is removed. Any rule that still references markers via `parts.yaml` fails fast. The `parts.yaml::markers` block remains in place for backward-compatibility of any external readers but is no longer read by the engine. | Begins at first release after Phase A is observed to emit zero warnings. |
| **C. Removal** | The `markers:` block is deleted from `parts.yaml`. The `parts.schema.json` may optionally drop the `role: marker` enum value (not necessary; harmless). | At the next major release after Phase B (v0.3.0 candidate). |

A new CI gate (§ 4.3) tracks the WARN-level shim hits across the dual-read window so the cut-over decision is data-driven, not date-driven.

---

## 4. CI gates

### 4.1 `markers-citation-presence-check`

- **Purpose:** Every marker in `catalogues/markers.yaml` must have a `citation` block with `grade: A1 | A2 | A3 | B1 | B2` (no `C`-grade for canonical entries; `C` is reserved for unverified discovery-only data which has no place in a runtime catalogue).
- **Implementation:** `tools/ci/markers_citation_presence_check.py`. Validates each `items[].citation`, each `items[].working_concentrations[].citation`, and (if present) `items[].counter_selection.citation`.
- **Auxiliary check:** Warns if `class: yeast_auxotrophic` is combined with non-zero `concentration_ugml` (catches accidental "100 μg/mL URA3" entries).
- **Lifecycle:** Lands in `enforced` mode at the same time as `catalogues/markers.yaml` itself (one PR atomicity).

### 4.2 `host-marker-link-integrity-check`

- **Purpose:** Every `recommended_selection_markers[]` entry in `catalogues/hosts.yaml` must resolve to an existing `marker_id` in `catalogues/markers.yaml`.
- **Implementation:** `tools/ci/host_marker_link_integrity_check.py`. Loads both YAMLs, collects all marker IDs, validates every link.
- **Lifecycle:** Lands in `enforced` mode the same PR as the first `recommended_selection_markers[]` field is written into a host record.

### 4.3 `ml-corpus-license-check`

- **Purpose:** Every record under `docs/ml_corpus/records/**/*.json` must carry a `license` block with both `redistribution_allowed: bool` and `ml_training_allowed: bool` set **explicitly**. Missing-or-default is a hard fail. Records with `ml_training_allowed: false` may exist in the corpus directory but must be in `exclusions.yaml`, not `records/`.
- **Auxiliary check (shim-hit telemetry, dual-read instrumentation):** This same script (or a sibling) also counts WARN-level "marker-fell-back-to-parts.yaml" log lines emitted during the dual-read window. Output is appended to `docs/handover/dual_read_shim_hits.log` and surfaced in `TASK_BOARD.md`.
- **Implementation:** `tools/ci/ml_corpus_license_check.py`.
- **Lifecycle:** Lands in `enforced` mode at the same time as the first record is committed to `docs/ml_corpus/records/`.

### 4.4 Extensions to `tools/agenda_consistency_check.py`

| Check addition | Purpose |
|---|---|
| `EXPECTED_TOTAL` bump | Updated to whatever the new task-card count becomes after CODING_AGENDA step 9. Until step 9, this remains 71. The check tolerates a `# pending-step-9` comment block. |
| `EXPECTED_PHASE_X` extension | New task IDs added to the appropriate phase list (TBD by dev-orchestrator — see § 6 Q1). |
| `STALE_IDS` extension | Add `T-MARKERS-PARTS-SHIM` (or similar) once the dual-read window closes, to catch any new code referencing the retired shim. |
| New: port-count consistency | Asserts `len(port_manifest.yaml::ports) == ARCHITECTURE.md § 4.5 canonical-port-count`. Catches the recurring drift problem that produced the "50 vs 56" discrepancy in user memory. |
| New: schema-version monotonicity | Asserts each catalogue's `schema_version` is ≥ the version recorded in the previous commit. |
| New: hosts-v1.1-field-coverage | Soft check (warns, not fails): for any host record with `t7_lysogen != null`, verify `protease_status` and `disulfide_environment` are also present (so we don't end up with half-populated v1.1 records). |

---

## 5. ML-corpus subsystem governance

### 5.1 Canonical folder layout

```
docs/ml_corpus/
├── README.md                                    # Purpose, scope, license matrix, exclusion criteria.
├── corpus_manifest.yaml                         # Aggregate manifest: counts, license breakdown, cross-check coverage.
├── exclusions.yaml                              # Records considered + rejected, with reason.
├── crosscheck_log.yaml                          # Append-only log of SnapGene cross-checks (date, checker, record, outcome).
├── schemas/
│   └── corpus_record.schema.json                # Per § 2.3 of this analysis.
└── records/
    ├── backbones/
    │   ├── ecoli/                               # pUC, pBR322, pET, pBAD, pCDF, pRSF, pACYC, pGEX, pMAL, pTrc...
    │   ├── kphaffii/                            # pPICZ, pPIC, pAO815, pGAPZ...
    │   ├── scerevisiae/                         # pYES2, pRS, p2μ, YIp, YEp, YCp...
    │   └── mammalian/                           # pcDNA, pLenti, pAAV, pCMV, pIRES, pHR'...
    └── elements/
        ├── promoters/
        ├── terminators/
        ├── rbs_kozak/
        ├── polyA/
        ├── ires_2a/
        ├── mcs/
        ├── tags/
        ├── fluorescent_proteins/
        ├── selection_cassettes/
        ├── insulators/
        └── introns_wpre/
```

`README.md` of `docs/ml_corpus/` mirrors the standing working-principle § 0 at its top (so a researcher who opens the folder cold sees the cadence) and explicitly states:

> This folder is **training data**, not runtime configuration. It is read by tooling for ML model training and analytics only. The runtime engine **must not** import from this folder; the `import-linter` rule below enforces this.

### 5.2 SnapGene cross-check — **process-only artefact (architecture decision)**

**Decision: Process-only artefact. NOT a runtime gate. NOT a CI hard fail.**

Reasoning:

1. **The cross-check is human judgement.** Decision #4 explicitly says "manual cross-check". Automating it requires either scraping SnapGene (forbidden) or licensed access to a SnapGene-internal API (not available). A human-judgement step can't be a deterministic gate.
2. **CI gates should be deterministic from in-tree data.** Anything CI checks must be reproducible from a clean checkout. A "look this up on SnapGene" requirement isn't reproducible.
3. **It's QC, not validation.** The cross-check verifies that *we* haven't introduced a transcription error during ingestion. The downstream ML training tolerates a small fraction of un-cross-checked records (they get a confidence-weighted treatment); a missing cross-check is not a correctness failure of the system, only of the curation pass.
4. **Soft incentive is preferable.** The `corpus_manifest.yaml` aggregate reports cross-check coverage (e.g., "183 / 247 records cross-checked, 74%") and that number is surfaced in `TASK_BOARD.md`. Coverage approaching 100% becomes a release-blocking criterion for the corpus's *publication*, not for individual record acceptance.

Mechanism in code:

| Artefact | Role |
|---|---|
| `snapgene_crosscheck` field in each record | Records the per-record check status. `checked: false` is valid. |
| `docs/ml_corpus/crosscheck_log.yaml` | Append-only log of cross-checks performed (researcher, date, record id, outcome, discrepancy resolution if any). |
| `corpus_manifest.yaml::crosscheck_coverage` | Aggregate %. Recomputed by `tools/ci/ml_corpus_license_check.py` on every CI run. |
| `tools/ci/ml_corpus_license_check.py` | Emits a CI **warning** (not failure) when corpus-wide coverage drops below a threshold (proposed 60% for v0.1 corpus, ratcheting upward at each release). |
| Release-blocking criterion (separate from CI) | A corpus *release tag* (e.g., `cev-mlcorpus-v0.1`) requires coverage ≥ 90% — this is enforced by `tools/release/corpus_release_gate.py`, run only at release time. |

### 5.3 Runtime / training-data boundary — **re-affirmed and enforced**

The ML corpus is **training data**, not runtime configuration. The boundary is enforced at three layers:

1. **File-tree layer.** `docs/ml_corpus/` sits outside `catalogues/` and outside `schemas/`.
2. **Import-linter layer.** Add to `pyproject.toml` (or wherever `import-linter` is configured):
   ```toml
   [[tool.importlinter.contracts]]
   name = "ml-corpus-is-not-runtime"
   type = "forbidden"
   source_modules = ["src.*"]
   forbidden_modules = ["docs.ml_corpus.*"]
   ```
3. **Data-shape layer.** The corpus manifest format (`corpus_manifest.yaml`) is structurally different from runtime catalogue manifests (no `catalogue_id`, no `items:` array, uses `records:` keyed by id with metadata-heavy structure) so accidental cross-use produces a schema validation error.

The training pipeline lives in a separate top-level folder (proposed: `ml/` or `training/`) that imports from `docs/ml_corpus/` but never from `catalogues/`. That folder is *out of scope* for this enrichment task and would be its own work track in a future cadence.

---

## 6. Risk + open questions for the three-skill joint plan (step 7)

The following items are deliberately left open for resolution at step 7, where `/scientific-advisor` + `/dev-orchestrator` + `/architect` decide together.

| # | Question | Why it's open |
|---|---|---|
| **Q1** | Where do the new task cards live? | Phase 4 ("Catalogues") was the natural home but is marked complete. Three options: (a) **Phase 4 extension** — append T-407 (markers catalogue loader), T-408 (host schema v1.1), T-409 (ml-corpus subsystem) under Phase 4 with a "Phase 4.2" sub-marker. (b) **New Phase 14** — "Post-v0.1.0 catalogue enrichment". (c) **Split** — Tracks A+B as a Phase 4 extension, Track C as a new Phase 14. Recommendation lean: option (c) because the runtime catalogue work and the ML-corpus subsystem have different governance, but dev-orchestrator owns this call. |
| **Q2** | New MR/WR/BR/SR rules from the enrichment? | Each new strain phenotype (T7 lysogen, protease, disulfide, methylation) may motivate new rule predicates (e.g., "MR-METHYL-XbaI: XbaI digest of dam+ plasmid fails"). Scientific-advisor should enumerate which new rules are in-scope vs out-of-scope for this enrichment. |
| **Q3** | Port count drift | Adding `MarkersCataloguePort` is +1. If `/architect` previously planned six biological catalogue ports (per stale memory) that never landed in code, should those be added now (going from 50 → 57) or left out? Recommendation: **out of scope** for this enrichment. Address in a separate cadence. |
| **Q4** | Existing-record backfill | Should the existing host records (DH5α, TOP10, JM109, XL1-Blue, Stbl3, BL21 baseline, cell-free, yeast, mammalian, insect, plant, phage/VLP) be enriched with the new v1.1 fields, or left as-is and only new strains use the new fields? Recommendation: **deferred backfill** — create a follow-up CODING_AGENDA task T-408a for backfilling existing records, scheduled after the 30 new strains are written so the schema is exercised end-to-end first. |
| **Q5** | Cell-free hosts (PURE, myTXTL) field applicability | Do PURE / myTXTL records get any of the new fields? T7 lysogen is irrelevant (no genome); protease and disulfide depend on PURE composition (defined-component, T7 RNAP added). Recommendation: leave existing cell-free records unchanged and add a `chassis_class: "cell_free"` discriminator that exempts them from the v1.1 backfill. |
| **Q6** | ML-corpus git LFS | Individual records will be ~few KB each (JSON + GFF3 annotation). Total at v0.1 corpus size (~350 records) is well under 100 MB and fits comfortably in git. Aggregated training bundles (tar.gz of all records) are different and may belong in LFS. Recommendation: **in-tree per record, LFS for release bundles**. |
| **Q7** | iGEM CC-BY-SA contagion | Some iGEM parts are CC-BY-SA. Mixing CC-BY-SA records into an ML training corpus may impose share-alike on derivatives (the trained model itself). `/ip-auditor` (step 4 in parallel) must rule on this. Architecture recommendation: tag CC-BY-SA records with `license.notes: "share-alike — review before mixing into commercial derivatives"` and route them to a `records/cc-by-sa/` subfolder so they can be excluded from training runs if needed. |
| **Q8** | Sequence vs annotation independence | A backbone sequence may be public-domain (NCBI/INSDC) while its annotation may have been authored by a vendor or by SnapGene. The schema currently bundles both in one license block. Should we split into `sequence_license` + `annotation_license`? Recommendation: **yes** — extend the license block in a v1.0.1 schema bump if `/ip-auditor` confirms divergent posture. |
| **Q9** | Working-concentration regional variation | Sambrook's concentrations are sometimes lab-tradition rather than rigorously empirical, and some labs use 2× the Sambrook value to suppress satellite colonies. Should the markers schema's `concentration_ugml.typical` be Sambrook-default, or carry a `regional_variants[]` block? Recommendation: Sambrook-default with `notes:` field carrying variant info; defer per-lab override to institutional policy. |
| **Q10** | Initial markers count | The initial report mentions ~9 bacterial + ~6 auxotrophic + ~4 dominant yeast = 19 markers as the v0.1 markers catalogue. Should we add mammalian markers (puromycin, blasticidin, hygromycin-mammalian, G418-mammalian) in the same pass, or defer to a follow-up? Recommendation: **in-scope now**, since the host coverage already includes mammalian rules in the existing catalogue; including mammalian markers in the v0.1 markers catalogue avoids a near-immediate v0.2 bump. |

---

## 7. Acceptance checklist (for the user)

Before this analysis is accepted (cadence step 5), please confirm or amend the following:

| # | Item | Default |
|---|---|---|
| AC-1 | Backward-compatible (all-optional) v1.1 fields on `hosts.schema.json`. | Accept. |
| AC-2 | New standalone `catalogues/markers.yaml` + `schemas/markers.schema.json` v1.0. | Accept. |
| AC-3 | Auxotrophic markers use sentinel `concentration_ugml: {min: 0, typical: 0, max: 0}` + warn-level CI check. | Accept (or amend to split-schema). |
| AC-4 | New `MarkersCataloguePort` slotting in as canonical port **#51**. | Accept. |
| AC-5 | Dual-read migration window for `parts.yaml::markers` (no hard cut-over). | Accept. |
| AC-6 | SnapGene cross-check is a **process-only artefact** — not a CI gate. | Accept. |
| AC-7 | ML corpus lives under `docs/ml_corpus/` with import-linter enforcement that `src/*` cannot read from it. | Accept. |
| AC-8 | All ten open questions Q1–Q10 above are deferred to the three-skill joint plan (step 7), not resolved in this analysis. | Accept. |
| AC-9 | This analysis can proceed to step 5 once `/ip-auditor` delivers its parallel step-4 analysis. | Accept. |

---

> **Disclaimer:** This architectural analysis is provided for informational and development purposes only. The schema fragments, port designs, and CI-gate proposals herein are design recommendations, not committed architecture; the binding `ARCHITECTURE.md` update happens at cadence step 8 and may revise these proposals in light of the joint planning step 7. All performance / scaling / complexity claims are derived from established design patterns in the existing v0.1.0 codebase (50-port hexagonal architecture, per-catalogue read-only ports, additive schema versioning), not from fabricated benchmarks. Production deployment of any schema or port change requires the full cadence (steps 5–10) and the existing audit-traceability + agenda-consistency CI surface to remain green.
