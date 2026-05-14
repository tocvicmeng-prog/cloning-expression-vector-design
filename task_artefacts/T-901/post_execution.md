# T-901 Post-Execution Notes

## Summary

Implemented `adapter.io.EmblAdapter` and `adapter.io.Gff3Adapter`.
EMBL uses the existing Biopython-backed feature conversion path with an
EMBL-specific qualifier namespace. GFF3 writes standards-shaped feature rows plus
an embedded FASTA section and reads only single-sequence embedded-FASTA GFF3
payloads, which keeps the adapter aligned with the project `ImportedConstruct`
contract.

## Files Changed

- `src/adapter/io/embl.py`
- `src/adapter/io/gff3.py`
- `src/adapter/io/_biopython.py`
- `src/adapter/io/__init__.py`
- `tests/adapter/io/test_sequence_io.py`
- `tasks/task_brief/T-901.md`
- `README.md`
- `ROADMAP.md`
- `CODING_AGENDA.md`
- `TASK_BOARD.md`

## Verification

- `python -m uv sync --frozen --no-editable --group dev --extra io --reinstall-package cloning-expression-vector-design` -> passed
- `python -m uv run --no-editable ruff check src\adapter\io\embl.py src\adapter\io\gff3.py src\adapter\io\_biopython.py src\adapter\io\__init__.py tests\adapter\io\test_sequence_io.py` -> passed
- `python -m uv run --no-editable ruff format --check src\adapter\io\embl.py src\adapter\io\gff3.py src\adapter\io\_biopython.py src\adapter\io\__init__.py tests\adapter\io\test_sequence_io.py` -> passed
- `python -m uv run --no-editable mypy src\adapter\io\embl.py src\adapter\io\gff3.py src\adapter\io\_biopython.py tests\adapter\io\test_sequence_io.py` -> passed
- `python -m uv run --no-editable pytest tests\adapter\io\test_sequence_io.py -q` -> 8 passed
- `python tools\agenda_consistency_check.py` -> passed
- `python -m uv run --no-editable ruff check .` -> passed
- `python -m uv run --no-editable mypy src tools tests` -> passed
- `python -m uv run --no-editable lint-imports --config .importlinter` -> 3 contracts kept
- `python -m uv run --no-editable python tools\ci\run_pytest.py -m "not slow"` -> 479 passed, 2 skipped

## Next

Open T-902 `adapter.snapgene.SnapGeneFileWatcher`.
