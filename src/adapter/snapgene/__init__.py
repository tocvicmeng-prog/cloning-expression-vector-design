"""
module_id: adapter.snapgene
file: src/adapter/snapgene/__init__.py
task_id: T-902,T-1203

SnapGene integration surface.
"""

from __future__ import annotations

from adapter.io import SnapGeneDnaReader, SnapGeneDnaReadError
from adapter.snapgene.api_client import (
    SnapGeneApiCapabilities,
    SnapGeneApiClient,
    SnapGeneApiError,
    SnapGeneApiExportResult,
    SnapGeneApiImportResult,
    SnapGeneApiRequestError,
    SnapGeneApiResponseError,
    SnapGeneApiSyncResult,
    SnapGeneApiUnavailableError,
    SnapGeneCommandTransport,
    SnapGeneRequestTransport,
    SnapGeneServerStatus,
    SnapGeneSvgMapResult,
)
from adapter.snapgene.file_watcher import (
    SnapGeneFileWatcher,
    SnapGeneWatchResult,
    UnsupportedSnapGeneWatchPathError,
)

__all__ = [
    "SnapGeneApiCapabilities",
    "SnapGeneApiClient",
    "SnapGeneApiError",
    "SnapGeneApiExportResult",
    "SnapGeneApiImportResult",
    "SnapGeneApiRequestError",
    "SnapGeneApiResponseError",
    "SnapGeneApiSyncResult",
    "SnapGeneApiUnavailableError",
    "SnapGeneCommandTransport",
    "SnapGeneDnaReadError",
    "SnapGeneDnaReader",
    "SnapGeneFileWatcher",
    "SnapGeneRequestTransport",
    "SnapGeneServerStatus",
    "SnapGeneSvgMapResult",
    "SnapGeneWatchResult",
    "UnsupportedSnapGeneWatchPathError",
]
