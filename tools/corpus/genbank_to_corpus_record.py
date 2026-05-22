"""
module_id:           tools.corpus.genbank_to_corpus_record
file:                tools/corpus/genbank_to_corpus_record.py
task_id:             T-1404
architecture_refs:   ARCHITECTURE.md § 9.3 ML Training Corpus Subsystem; § 9.6 Fork-Readiness
requirements_refs:   FR-ML-01..15
citations:           v0.2 Enrichment Amendment (2026-05-23); joint plan § 4 T-1404
purity:              tool (file I/O + GenBank parsing + corpus_record YAML emission)

GenBank flat-file → corpus_record YAML converter.

Reads an NCBI eutils-fetched GenBank record (rettype=gb&retmode=text) and emits
a corpus_record schema-conformant YAML file under docs/ml_corpus/records/.

Provenance defaults:
- source = ncbi_genbank (override with --source for non-NCBI deposits)
- sequence + annotation license = "INSDC-policy / public-domain"
- snapgene_crosscheck.checked = False (pending human SnapGene cross-check per BR-16)

Usage:
    python tools/corpus/genbank_to_corpus_record.py \
        --in /tmp/genbank/pUC19_L09137.gb \
        --out docs/ml_corpus/records/backbones/ecoli/pUC19_L09137.yaml \
        --id corpus.backbone.ecoli.puc19 \
        --host-class ecoli \
        --replicon pMB1 \
        --copy-number high \
        --intended-use cloning,subcloning

The schema lives at docs/ml_corpus/schemas/corpus_record.schema.json (T-1402).
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import yaml


def parse_locus(line: str) -> dict[str, object]:
    parts = line.split()
    return {
        "locus_name": parts[1],
        "length_bp": int(parts[2]),
        "topology": "circular" if "circular" in line.lower() else "linear",
    }


def parse_accession(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("ACCESSION"):
            parts = line[12:].strip().split()
            if parts:
                return parts[0]
    return ""


def parse_definition(lines: list[str]) -> str:
    out: list[str] = []
    for line in lines:
        if line.startswith("DEFINITION"):
            out.append(line[12:].strip())
        elif out and line.startswith(" "):
            out.append(line.strip())
        elif out:
            break
    return " ".join(out).rstrip(".")


def parse_organism(lines: list[str]) -> str:
    for i, line in enumerate(lines):
        if line.startswith("  ORGANISM"):
            return line[12:].strip()
    return ""


def parse_pmids(lines: list[str]) -> list[str]:
    pmids: list[str] = []
    for line in lines:
        m = re.search(r"PUBMED\s+(\d+)", line)
        if m:
            pmids.append(m.group(1))
    return pmids


def parse_features(lines: list[str]) -> list[dict[str, object]]:
    """Parse the FEATURES section. Skip 'source' (redundant with LOCUS)."""
    features: list[dict[str, object]] = []
    in_features = False
    current: dict[str, object] | None = None
    current_qual_key: str | None = None
    for line in lines:
        if line.startswith("FEATURES"):
            in_features = True
            continue
        if in_features and line.startswith("ORIGIN"):
            break
        if not in_features:
            continue
        if line.startswith("     ") and not line.startswith("                     "):
            # Feature start: "     gene            123..456"
            if current is not None and current["type"] != "source":
                features.append(current)
            current_qual_key = None
            parts = line[5:].split(None, 1)
            if len(parts) < 2:
                current = None
                continue
            ftype, location = parts[0], parts[1].strip()
            strand = "-" if "complement(" in location else "+"
            # Strip complement(), join() etc. for a coarse start/end
            loc_clean = re.sub(r"[^0-9.,]", "", location).strip(",.")
            range_match = re.search(r"(\d+)\.\.(\d+)", loc_clean)
            if range_match:
                start, end = int(range_match.group(1)), int(range_match.group(2))
            else:
                single = re.search(r"(\d+)", loc_clean)
                if single:
                    start = end = int(single.group(1))
                else:
                    start = end = 0
            current = {
                "type": ftype,
                "start": start,
                "end": end,
                "strand": strand,
                "qualifiers": {},
                "_raw_location": location,
            }
        elif line.startswith("                     ") and current is not None:
            # Qualifier line: "                     /gene=\"bla\""
            qual_line = line.strip()
            if qual_line.startswith("/"):
                m = re.match(r"/([^=]+)=?(.*)", qual_line)
                if m:
                    current_qual_key = m.group(1)
                    val = m.group(2).strip().strip('"')
                    current["qualifiers"][current_qual_key] = val
            elif current_qual_key:
                current["qualifiers"][current_qual_key] = (
                    str(current["qualifiers"].get(current_qual_key, "")) + " " + qual_line.strip('"')
                ).strip()
    if current is not None and current["type"] != "source":
        features.append(current)
    # Drop the _raw_location helper before emission
    for f in features:
        f.pop("_raw_location", None)
    return features


def parse_origin(lines: list[str]) -> str:
    bases: list[str] = []
    in_origin = False
    for line in lines:
        if line.startswith("ORIGIN"):
            in_origin = True
            continue
        if not in_origin:
            continue
        if line.startswith("//"):
            break
        bases.append(re.sub(r"[^A-Za-z]", "", line).upper())
    return "".join(bases)


def build_record(
    gb_path: Path,
    *,
    record_id: str,
    host_class: str,
    replicon: str | None,
    copy_number: str | None,
    intended_use: list[str],
    source: str,
    snapgene_record_name: str | None,
) -> dict[str, object]:
    lines = gb_path.read_text(encoding="utf-8").splitlines()
    locus = parse_locus(lines[0])
    accession = parse_accession(lines)
    definition = parse_definition(lines)
    organism = parse_organism(lines)
    pmids = parse_pmids(lines)
    features = parse_features(lines)
    bases = parse_origin(lines)

    sha256 = hashlib.sha256(bases.encode("ascii")).hexdigest()

    record: dict[str, object] = {
        "id": record_id,
        "category": "backbone",  # overridden post-build via record["category"] if --category passed
        "sequence": {
            "bases": bases,
            "topology": str(locus["topology"]),
            "length_bp": int(locus["length_bp"]),
        },
        "annotation": features,
        "provenance": {
            "source": source,
            "accession_or_url": (
                f"https://www.ncbi.nlm.nih.gov/nuccore/{accession}"
                if source == "ncbi_genbank"
                else accession
            ),
            "retrieved_at": "2026-05-23",
            "retrieved_by": "T-1404 scientific-advisor curation via NCBI eutils efetch (rettype=gb)",
            "definition": definition,
            "organism": organism,
            "pmids": pmids,
            "notes": (
                "Machine-fetched from NCBI eutils efetch 2026-05-23; raw GenBank cached "
                "at /tmp/genbank/. Parser: tools/corpus/genbank_to_corpus_record.py. "
                "SnapGene cross-check pending per BR-16 NORMATIVE."
            ),
        },
        "license": {
            "sequence_license": {
                "spdx_id": "NCBI-PD",
                "redistribution_allowed": True,
                "ml_training_allowed": True,
                "attribution_required": False,
                "commercial_use_allowed": True,
                "source_text_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                "notes": (
                    "INSDC public-domain sequence policy: GenBank/ENA/DDBJ sequence "
                    "records are released under no-restriction terms. See IP-audit "
                    "§ 4.1 (NCBI/EBI/DDBJ tier-1 allowlist)."
                ),
            },
            "annotation_license": {
                "spdx_id": "NCBI-PD",
                "redistribution_allowed": True,
                "ml_training_allowed": True,
                "attribution_required": False,
                "commercial_use_allowed": True,
                "source_text_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                "notes": (
                    "INSDC submitter-deposited annotations are released under the same "
                    "no-restriction terms as the sequence. Curator-authored annotation "
                    "overlays (if any) are handled per IP-audit § 5.2."
                ),
            },
        },
        "snapgene_crosscheck": {
            "checked": False,
            "checker": "pending_human_curation",
            "snapgene_record_name": snapgene_record_name or "",
            "discrepancy_resolution": (
                "Cross-check pending. Per BR-16 NORMATIVE this is a human-in-browser "
                "step; no automated SnapGene access. Curator: open "
                + (snapgene_record_name or "the canonical SnapGene record")
                + " in browser, visually compare sequence + key annotations against this "
                "record's NCBI-fetched bases, log result in crosscheck_log.yaml."
            ),
        },
        "host_topology": {
            "host_class": host_class,
            "replicon": replicon or "",
            "copy_number_class": copy_number or "null",
        },
        "intended_use_category": intended_use,
        "checksum": {
            "algorithm": "sha256",
            "value": sha256,
        },
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_path", required=True, type=Path)
    parser.add_argument("--out", dest="output_path", required=True, type=Path)
    parser.add_argument("--id", dest="record_id", required=True)
    parser.add_argument("--host-class", required=True)
    parser.add_argument("--replicon", default=None)
    parser.add_argument(
        "--copy-number",
        choices=["high", "medium", "low", "single", "null"],
        default="null",
    )
    parser.add_argument("--intended-use", default="cloning")
    parser.add_argument("--source", default="ncbi_genbank")
    parser.add_argument("--snapgene-name", default=None)
    parser.add_argument(
        "--category",
        choices=[
            "backbone", "promoter", "terminator", "rbs", "kozak", "polyA",
            "ires", "2a_peptide", "mcs", "tag", "fluorescent_protein",
            "selection_cassette", "insulator", "wpre", "intron",
        ],
        default="backbone",
    )
    args = parser.parse_args()

    record = build_record(
        args.input_path,
        record_id=args.record_id,
        host_class=args.host_class,
        replicon=args.replicon,
        copy_number=args.copy_number,
        intended_use=args.intended_use.split(","),
        source=args.source,
        snapgene_record_name=args.snapgene_name,
    )
    record["category"] = args.category
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(
        yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    bases_len = len(record["sequence"]["bases"])  # type: ignore[index]
    expected = record["sequence"]["length_bp"]  # type: ignore[index]
    if bases_len != expected:
        print(
            f"WARN: bases length {bases_len} != LOCUS length_bp {expected} "
            f"({args.input_path.name})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
