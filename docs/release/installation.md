# Installation

## Requirements

- Python 3.11.15
- uv 0.11.14
- Windows, Linux, or macOS with a filesystem that supports SQLite WAL mode

## Local Development Install

```powershell
python -m pip install "uv==0.11.14"
python -m uv sync --frozen --no-editable --group dev --extra io
```

Run the local verification suite:

```powershell
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe tools\ci\run_pytest.py -m "not slow"
```

## Wheel Build

```powershell
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe -m tools.release.build_wheel --dist-dir dist
```

The wrapper pins `SOURCE_DATE_EPOCH` and `PYTHONHASHSEED` for reproducible wheel metadata.

## Container Build

```powershell
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe -m tools.release.build_container_image --tag cev-design:0.1.0
```

The Dockerfile pins Python 3.11.15, uv 0.11.14, the non-editable dependency sync, and bundled
canonical fonts.

## Runtime Entry Points

- `cev-design`
- `vector-design`
- `vector-design-api`
- `vector-design-admin-service`

