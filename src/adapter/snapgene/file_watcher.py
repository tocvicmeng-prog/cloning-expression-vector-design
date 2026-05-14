"""
module_id: adapter.snapgene.file_watcher
file: src/adapter/snapgene/file_watcher.py
task_id: T-902

Deterministic SnapGene file-watch channel.
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from adapter.io import GenBankAdapter, ImportedConstruct, SnapGeneDnaReader, WriteResult

SUPPORTED_INPUT_SUFFIXES = frozenset({".gb", ".gbk", ".genbank", ".dna"})


class UnsupportedSnapGeneWatchPathError(ValueError):
    """Raised when a watched path is not a supported SnapGene interchange file."""


class SnapGeneDnaReaderLike(Protocol):
    def read_dna(self, source: bytes) -> ImportedConstruct: ...


ValidationHook = Callable[[ImportedConstruct], ImportedConstruct | None]
ClockMs = Callable[[], int]


@dataclass(frozen=True)
class SnapGeneWatchResult:
    source_path: Path
    output_path: Path
    source_format: str
    imported: ImportedConstruct
    write_result: WriteResult


@dataclass(frozen=True)
class _DebouncedPath:
    path: Path
    timestamp_ms: int


class _DebounceQueue:
    def __init__(self, debounce_ms: int) -> None:
        if debounce_ms < 0:
            raise ValueError("debounce_ms must be non-negative")
        self._debounce_ms = debounce_ms
        self._latest_by_path: dict[Path, int] = {}

    def record_write(self, path: Path, timestamp_ms: int) -> None:
        self._latest_by_path[path] = timestamp_ms

    def flush_ready(self, now_ms: int) -> tuple[_DebouncedPath, ...]:
        ready: list[_DebouncedPath] = []
        for path, timestamp_ms in sorted(self._latest_by_path.items()):
            if now_ms - timestamp_ms >= self._debounce_ms:
                ready.append(_DebouncedPath(path=path, timestamp_ms=timestamp_ms))
        for event in ready:
            del self._latest_by_path[event.path]
        return tuple(ready)


class SnapGeneFileWatcher:
    """Pollable SnapGene channel for GenBank and read-only SnapGene .dna files."""

    def __init__(
        self,
        watch_dir: Path | str,
        output_dir: Path | str,
        *,
        debounce_ms: int = 250,
        poll_interval_ms: int = 100,
        genbank_adapter: GenBankAdapter | None = None,
        snapgene_dna_reader: SnapGeneDnaReaderLike | None = None,
        validation_hook: ValidationHook | None = None,
        clock_ms: ClockMs | None = None,
    ) -> None:
        self.watch_dir = Path(watch_dir)
        self.output_dir = Path(output_dir)
        self.poll_interval_ms = poll_interval_ms
        self._genbank_adapter = genbank_adapter or GenBankAdapter()
        self._snapgene_dna_reader = snapgene_dna_reader or SnapGeneDnaReader()
        self._validation_hook = validation_hook
        self._clock_ms = clock_ms or _monotonic_ms
        self._debounce = _DebounceQueue(debounce_ms)
        self._signatures_by_path: dict[Path, tuple[int, int]] = {}
        if self.poll_interval_ms < 0:
            raise ValueError("poll_interval_ms must be non-negative")
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.watch_dir.resolve() == self.output_dir.resolve():
            raise ValueError("watch_dir and output_dir must be different directories")

    def record_write(self, path: Path | str, *, timestamp_ms: int | None = None) -> None:
        watched_path = Path(path)
        _require_supported_path(watched_path)
        if not watched_path.exists():
            raise FileNotFoundError(watched_path)
        event_time_ms = timestamp_ms if timestamp_ms is not None else self._clock_ms()
        self._debounce.record_write(watched_path, event_time_ms)

    def scan(self, *, now_ms: int | None = None) -> None:
        timestamp_ms = now_ms if now_ms is not None else self._clock_ms()
        for path in self._iter_supported_files(self.watch_dir):
            signature = _signature(path)
            if self._signatures_by_path.get(path) == signature:
                continue
            self._signatures_by_path[path] = signature
            self._debounce.record_write(path, timestamp_ms)

    def flush_ready(self, *, now_ms: int | None = None) -> tuple[SnapGeneWatchResult, ...]:
        timestamp_ms = now_ms if now_ms is not None else self._clock_ms()
        ready_paths = self._debounce.flush_ready(timestamp_ms)
        return tuple(self._process_path(event.path) for event in ready_paths)

    def poll_once(self, *, now_ms: int | None = None) -> tuple[SnapGeneWatchResult, ...]:
        timestamp_ms = now_ms if now_ms is not None else self._clock_ms()
        self.scan(now_ms=timestamp_ms)
        return self.flush_ready(now_ms=timestamp_ms)

    def watch(self, path: str) -> Iterable[SnapGeneWatchResult]:
        self.watch_dir = Path(path)
        while True:
            yield from self.poll_once()
            time.sleep(self.poll_interval_ms / 1000)

    def _process_path(self, path: Path) -> SnapGeneWatchResult:
        _require_supported_path(path)
        source = path.read_bytes()
        if path.suffix.lower() == ".dna":
            imported = self._snapgene_dna_reader.read_dna(source)
            source_format = "snapgene-dna"
        else:
            imported = self._genbank_adapter.read(source)
            source_format = "genbank"
        validated = self._validation_hook(imported) if self._validation_hook else imported
        construct = validated or imported
        write_result = self._genbank_adapter.write(construct)
        output_path = self._output_path_for(path)
        _atomic_write(output_path, write_result.data)
        return SnapGeneWatchResult(
            source_path=path,
            output_path=output_path,
            source_format=source_format,
            imported=construct,
            write_result=write_result,
        )

    def _output_path_for(self, source_path: Path) -> Path:
        return self.output_dir / f"{source_path.stem}.gb"

    @staticmethod
    def _iter_supported_files(path: Path) -> tuple[Path, ...]:
        return tuple(
            sorted(
                candidate
                for candidate in path.iterdir()
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_INPUT_SUFFIXES
            )
        )


def _signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


def _require_supported_path(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
        raise UnsupportedSnapGeneWatchPathError(
            f"unsupported SnapGene watch target suffix: {path.suffix or '<none>'}"
        )


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False,
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(data)
    temp_path.replace(path)


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000
