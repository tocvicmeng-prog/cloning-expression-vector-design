# Migration From v0.0 To v0.1

v0.1.0 is the first complete local implementation line for this repository. Existing v0.0 users
should treat the release as a schema boundary rather than an in-place data migration.

## Project Data

- Recreate project sessions through the v0.1.0 CLI/API rather than loading prototype snapshots.
- Re-export sequence artefacts as GenBank, FASTA, SBOL3, EMBL, or GFF3 before moving data across.
- Verify construct hashes after import; v0.1.0 binds feature tables to canonical graph state.

## Authorisation And Audit Data

- Mint fresh signed `AuthorisationProfile` records with the v0.1.0 admin-service boundary.
- Do not copy prototype audit rows into the v0.1.0 SQLite audit log. The release audit log is an
  HMAC-chained append-only store and must start from a controlled key provider.
- Re-provision profile, SOP-template, and decision-record signing keys through the v0.1.0 key
  lifecycle tools.

## SOP Templates

- Re-bootstrap SOP templates into the signed SQLite SOP-template store.
- Unsigned or tampered templates fail closed and cannot be used for SOP rendering.

## Validation

After migration, run:

```powershell
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe tools\ci\run_pytest.py -m "not slow"
```

Then run the three white-paper UAT fixtures and the 100-realisation library benchmark before using
the environment for institutional review.
