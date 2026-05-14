# Platform Caveats

Project databases should not live inside actively syncing folders such as OneDrive. The default operational policy is to keep SQLite databases outside active sync paths and to treat OneDrive-backed paths as an experimental smoke-test surface only.

Local checks in this workspace use non-editable `uv` installs:

```powershell
python -m uv sync --frozen --no-editable --group dev --extra io
python -m uv run --no-editable python tools/ci/run_pytest.py -m "not slow"
```

The T-205 platform suite covers sync-like paths containing spaces and non-ASCII characters, SQLite WAL concurrency, atomic writes, spawn-based multiprocessing, debounce primitives, and IPC path shape checks. The active OneDrive smoke test is skipped unless `CEV_ACTIVE_ONEDRIVE_PATH` points at a real actively syncing directory.
