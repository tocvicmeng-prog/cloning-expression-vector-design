# Catalogue Loader Contract

T-401 establishes the common path used by all Phase-4 catalogue population tasks.

## Loader

Use `adapter.catalogue.load_catalogue(path, schema_path)` for every YAML catalogue. The loader:

- reads YAML with `yaml.safe_load`;
- rejects non-mapping roots;
- validates the document against the registered JSON Schema;
- parses the top-level `maintenance` block into `MaintenanceMetadata`;
- returns the original payload plus parsed maintenance metadata.

Use `adapter.catalogue.schema_for_catalogue(path, "schemas")` when loading project catalogues. If a new catalogue file name is added in later tasks, register it in `adapter.catalogue.yaml_loader._SCHEMA_BY_FILE` and add the matching schema under `schemas/`.

## Required YAML Fields

Every catalogue document must include:

- `catalogue_id`: stable machine id;
- `schema_version`: semantic version for the catalogue schema;
- `maintenance.retrieved_at`;
- `maintenance.valid_until`;
- `maintenance.review_required_after`;
- `maintenance.source_url`;
- a non-empty data collection for that catalogue family.

Dates are ISO `YYYY-MM-DD` strings. The stale-catalogue gate treats a catalogue as stale when either `valid_until` or `review_required_after` has passed.

## Citations

Catalogue citations use the shared `GradedCitation` shape:

- `text`;
- `grade`: `A1`, `A2`, `A3`, `B1`, `B2`, or `C`;
- `accessed`;
- optional `pmid`, `doi`, `pmc`, `url`.

The `source-grade-citation-check` gate accepts grades `A1` through `B2` directly. Grade `C` is allowed only when the citation object carries an explicit `corroborator` field.

## Downstream Rules

T-402 through T-406 should modify catalogue YAML and schemas together. A catalogue entry is not complete until it passes:

```powershell
python -m uv run --no-editable pytest tests/adapter/catalogue tests/ci_gates/test_t401_catalogue_gates.py
python tools/ci_gates/stale_catalogue_check.py
python tools/ci_gates/source_grade_citation_check.py
```

The Phase-4 exit can only enforce these gates after the populated catalogues and rule fixtures are present.
