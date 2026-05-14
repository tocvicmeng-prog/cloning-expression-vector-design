"""
module_id: tests.platform
file: tests/conftest_platform.py
task_id: T-205
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncLikePath:
    path: Path


@dataclass(frozen=True)
class ActiveSyncPath:
    path: Path


def make_sync_like_path(base: Path) -> SyncLikePath:
    path = base / "tmp_with space 文档" / "deep" / "nested"
    path.mkdir(parents=True, exist_ok=True)
    return SyncLikePath(path)


def active_sync_path_from_env() -> ActiveSyncPath | None:
    raw_path = os.environ.get("CEV_ACTIVE_ONEDRIVE_PATH")
    if not raw_path:
        return None
    path = Path(raw_path)
    return ActiveSyncPath(path) if path.exists() else None
