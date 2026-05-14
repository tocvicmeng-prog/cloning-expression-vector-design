"""
module_id: adapter.snapgene.api_client
file: src/adapter/snapgene/api_client.py
task_id: T-1203

SnapGene Server Request API client with file-watch fallback.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, TypeAlias, cast

from adapter.io import GenBankAdapter, ImportedConstruct, WriteResult
from adapter.snapgene.file_watcher import SnapGeneFileWatcher, SnapGeneWatchResult

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

SUCCESS_CODE = 0
UNAVAILABLE_LICENSE_TOKENS = frozenset(
    {
        "expired",
        "invalid",
        "missing",
        "not found",
        "not valid",
        "unavailable",
    }
)


class SnapGeneRequestTransport(Protocol):
    """Transport for a single SnapGene Server JSON request."""

    def request(self, payload: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]: ...


class SnapGeneApiError(RuntimeError):
    """Base class for SnapGene live API errors."""


class SnapGeneApiUnavailableError(SnapGeneApiError):
    """Raised when the live API cannot be used and no fallback is available."""


class SnapGeneApiResponseError(SnapGeneApiError):
    """Raised when a server response is malformed or mismatched."""


class SnapGeneApiRequestError(SnapGeneApiError):
    """Raised when SnapGene Server returns a non-zero response code."""

    def __init__(
        self,
        request_name: str,
        response_code: int,
        response_message: str,
        response: Mapping[str, JsonValue],
    ) -> None:
        self.request_name = request_name
        self.response_code = response_code
        self.response_message = response_message
        self.response = dict(response)
        message = (
            f"SnapGene request {request_name!r} failed with code {response_code}: "
            f"{response_message}"
        )
        super().__init__(message)


@dataclass(frozen=True)
class SnapGeneCommandTransport:
    """Transport that shells out to SnapGene Server's bundled request tool."""

    command: tuple[str, ...]
    timeout_seconds: float = 30.0

    def __init__(self, command: Sequence[str], timeout_seconds: float = 30.0) -> None:
        if not command:
            raise ValueError("command cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        object.__setattr__(self, "command", tuple(command))
        object.__setattr__(self, "timeout_seconds", timeout_seconds)

    def request(self, payload: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        encoded = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"))
        try:
            completed = subprocess.run(
                [*self.command, "-c", encoded],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SnapGeneApiUnavailableError(str(exc)) from exc
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or f"exit status {completed.returncode}"
            raise SnapGeneApiUnavailableError(stderr)
        return _loads_json_object(completed.stdout)


@dataclass(frozen=True)
class SnapGeneServerStatus:
    server_version: str | None
    request_count: int | None
    last_request: str | None
    uptime: str | None
    license_state: str | None
    license_expiration: str | None
    server_index: int | None
    raw_response: Mapping[str, JsonValue]


@dataclass(frozen=True)
class SnapGeneApiCapabilities:
    live_api: bool
    file_watch_fallback: bool
    reason: str
    server_version: str | None = None
    license_state: str | None = None


@dataclass(frozen=True)
class SnapGeneApiImportResult:
    input_genbank_path: Path
    output_dna_path: Path
    write_result: WriteResult
    response: Mapping[str, JsonValue]


@dataclass(frozen=True)
class SnapGeneApiExportResult:
    input_dna_path: Path
    output_genbank_path: Path
    imported: ImportedConstruct
    response: Mapping[str, JsonValue]


@dataclass(frozen=True)
class SnapGeneSvgMapResult:
    input_dna_path: Path
    output_svg_dom_path: Path
    svg_dom: str
    response: Mapping[str, JsonValue]


@dataclass(frozen=True)
class SnapGeneApiSyncResult:
    mode: str
    imported: ImportedConstruct
    live_import: SnapGeneApiImportResult | None = None
    live_export: SnapGeneApiExportResult | None = None
    fallback_watch: SnapGeneWatchResult | None = None
    fallback_reason: str | None = None


class SnapGeneApiClient:
    """Client for existing SnapGene Server installations.

    The public SnapGene product currently has no third-party API. This client is
    intentionally inert until a licensed SnapGene Server request transport is
    configured, and it can route work through the UR-01a file-watch channel when
    the live request API is unavailable.
    """

    def __init__(
        self,
        *,
        transport: SnapGeneRequestTransport | None = None,
        scratch_dir: Path | str | None = None,
        fallback_channel: SnapGeneFileWatcher | None = None,
        genbank_adapter: GenBankAdapter | None = None,
    ) -> None:
        self._transport = transport
        self.scratch_dir = (
            Path(scratch_dir) if scratch_dir is not None else Path(tempfile.mkdtemp())
        )
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self._fallback_channel = fallback_channel
        self._genbank_adapter = genbank_adapter or GenBankAdapter()

    def status(self) -> SnapGeneServerStatus:
        response = self._request("status", require_transport=True, check_response_code=False)
        if _response_code(response) not in (None, SUCCESS_CODE):
            raise SnapGeneApiRequestError(
                "status",
                _response_code(response) or -1,
                _response_message(response),
                response,
            )
        return SnapGeneServerStatus(
            server_version=_optional_str(response.get("serverVersion")),
            request_count=_optional_int(response.get("requestCount")),
            last_request=_optional_str(response.get("lastRequest")),
            uptime=_optional_str(response.get("uptime")),
            license_state=_optional_str(response.get("license")),
            license_expiration=_optional_str(response.get("licenseExpiration")),
            server_index=_optional_int(response.get("serverIndex")),
            raw_response=dict(response),
        )

    def capabilities(self) -> SnapGeneApiCapabilities:
        if self._transport is None:
            return SnapGeneApiCapabilities(
                live_api=False,
                file_watch_fallback=self._fallback_channel is not None,
                reason="SnapGene live API transport is not configured",
            )
        try:
            status = self.status()
        except SnapGeneApiError as exc:
            return SnapGeneApiCapabilities(
                live_api=False,
                file_watch_fallback=self._fallback_channel is not None,
                reason=str(exc),
            )
        if _license_is_unavailable(status.license_state):
            return SnapGeneApiCapabilities(
                live_api=False,
                file_watch_fallback=self._fallback_channel is not None,
                reason="SnapGene Server license is unavailable",
                server_version=status.server_version,
                license_state=status.license_state,
            )
        return SnapGeneApiCapabilities(
            live_api=True,
            file_watch_fallback=self._fallback_channel is not None,
            reason="SnapGene Server Request API is available",
            server_version=status.server_version,
            license_state=status.license_state,
        )

    def push_construct(
        self,
        construct: ImportedConstruct,
        *,
        output_dna_path: Path | str | None = None,
        enzyme_set: str | None = None,
        min_orf_len: int | None = None,
        reading_frames: str | None = None,
    ) -> SnapGeneApiImportResult:
        self._require_live_api()
        input_path = self.scratch_dir / f"{_safe_stem(construct.construct_id)}.gb"
        dna_path = (
            Path(output_dna_path) if output_dna_path is not None else input_path.with_suffix(".dna")
        )
        write_result = self._genbank_adapter.write(construct)
        _atomic_write(input_path, write_result.data)
        request_payload: JsonObject = {
            "inputFile": str(input_path),
            "outputFile": str(dna_path),
        }
        if enzyme_set is not None:
            request_payload["enzymeSet"] = enzyme_set
        if min_orf_len is not None:
            request_payload["minORFLen"] = min_orf_len
        if reading_frames is not None:
            request_payload["readingFrames"] = reading_frames
        response = self._request("importDNAFile", request_payload)
        return SnapGeneApiImportResult(
            input_genbank_path=input_path,
            output_dna_path=dna_path,
            write_result=write_result,
            response=response,
        )

    def pull_construct(
        self,
        input_dna_path: Path | str,
        *,
        output_genbank_path: Path | str | None = None,
        export_filter: str | None = None,
    ) -> SnapGeneApiExportResult:
        self._require_live_api()
        dna_path = Path(input_dna_path)
        output_path = (
            Path(output_genbank_path)
            if output_genbank_path is not None
            else self.scratch_dir / f"{_safe_stem(dna_path.stem)}.gb"
        )
        request_payload: JsonObject = {
            "inputFile": str(dna_path),
            "outputFile": str(output_path),
        }
        if export_filter is not None:
            request_payload["exportFilter"] = export_filter
        response = self._request("exportDNAFile", request_payload)
        imported = self._genbank_adapter.read(output_path.read_bytes())
        return SnapGeneApiExportResult(
            input_dna_path=dna_path,
            output_genbank_path=output_path,
            imported=imported,
            response=response,
        )

    def sync_construct(
        self,
        construct: ImportedConstruct,
        *,
        allow_file_watch_fallback: bool = True,
    ) -> SnapGeneApiSyncResult:
        capabilities = self.capabilities()
        if capabilities.live_api:
            live_import = self.push_construct(construct)
            live_export = self.pull_construct(live_import.output_dna_path)
            return SnapGeneApiSyncResult(
                mode="live_api",
                imported=live_export.imported,
                live_import=live_import,
                live_export=live_export,
            )
        if allow_file_watch_fallback and self._fallback_channel is not None:
            fallback = self._sync_via_file_watch(construct)
            return SnapGeneApiSyncResult(
                mode="file_watch_fallback",
                imported=fallback.imported,
                fallback_watch=fallback,
                fallback_reason=capabilities.reason,
            )
        raise SnapGeneApiUnavailableError(capabilities.reason)

    def generate_svg_map(
        self,
        input_dna_path: Path | str,
        *,
        linear: bool,
        output_svg_dom_path: Path | str | None = None,
        show_enzymes: bool = False,
        show_primers: bool = True,
        show_features: bool = True,
        show_orfs: bool = False,
        design_size: str | None = None,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> SnapGeneSvgMapResult:
        self._require_live_api()
        dna_path = Path(input_dna_path)
        svg_path = (
            Path(output_svg_dom_path)
            if output_svg_dom_path is not None
            else self.scratch_dir / f"{_safe_stem(dna_path.stem)}.svg"
        )
        request_payload: JsonObject = {
            "inputFile": str(dna_path),
            "linear": linear,
            "showEnzymes": show_enzymes,
            "showPrimers": show_primers,
            "showFeatures": show_features,
            "showORFs": show_orfs,
            "outputSvgDom": str(svg_path),
        }
        if design_size is not None:
            request_payload["designSize"] = design_size
        if title is not None:
            request_payload["title"] = title
        if subtitle is not None:
            request_payload["subtitle"] = subtitle
        response = self._request("generateSVGMap", request_payload)
        return SnapGeneSvgMapResult(
            input_dna_path=dna_path,
            output_svg_dom_path=svg_path,
            svg_dom=svg_path.read_text(encoding="utf-8"),
            response=response,
        )

    def fallback_channel(self) -> SnapGeneFileWatcher:
        if self._fallback_channel is None:
            raise SnapGeneApiUnavailableError("SnapGene file-watch fallback is not configured")
        return self._fallback_channel

    def _sync_via_file_watch(self, construct: ImportedConstruct) -> SnapGeneWatchResult:
        fallback = self.fallback_channel()
        input_path = fallback.watch_dir / f"{_safe_stem(construct.construct_id)}.gb"
        _atomic_write(input_path, self._genbank_adapter.write(construct).data)
        fallback.record_write(input_path, timestamp_ms=0)
        results = fallback.flush_ready(now_ms=1_000_000)
        if len(results) != 1:
            raise SnapGeneApiResponseError(
                f"SnapGene file-watch fallback produced {len(results)} results for {input_path}"
            )
        return results[0]

    def _require_live_api(self) -> None:
        capabilities = self.capabilities()
        if not capabilities.live_api:
            raise SnapGeneApiUnavailableError(capabilities.reason)

    def _request(
        self,
        request_name: str,
        parameters: Mapping[str, JsonValue] | None = None,
        *,
        require_transport: bool = True,
        check_response_code: bool = True,
    ) -> Mapping[str, JsonValue]:
        if self._transport is None:
            if require_transport:
                raise SnapGeneApiUnavailableError("SnapGene live API transport is not configured")
            return {}
        payload: JsonObject = {"request": request_name}
        payload.update(dict(parameters or {}))
        response = self._transport.request(payload)
        response_name = response.get("response")
        if response_name is not None and response_name != request_name:
            raise SnapGeneApiResponseError(
                f"SnapGene response {response_name!r} did not match request {request_name!r}"
            )
        if check_response_code:
            response_code = _response_code(response)
            if response_code is not None and response_code != SUCCESS_CODE:
                raise SnapGeneApiRequestError(
                    request_name,
                    response_code,
                    _response_message(response),
                    response,
                )
        return dict(response)


def _loads_json_object(source: str) -> Mapping[str, JsonValue]:
    try:
        parsed: Any = json.loads(source)
    except json.JSONDecodeError as exc:
        raise SnapGeneApiResponseError(f"SnapGene response was not JSON: {source!r}") from exc
    if not isinstance(parsed, dict):
        raise SnapGeneApiResponseError("SnapGene response must be a JSON object")
    return cast(Mapping[str, JsonValue], parsed)


def _response_code(response: Mapping[str, JsonValue]) -> int | None:
    for key in ("responseCode", "code"):
        value = response.get(key)
        if value is not None:
            return _optional_int(value)
    return None


def _response_message(response: Mapping[str, JsonValue]) -> str:
    message = response.get("responseMessage")
    if message is None:
        return "SnapGene Server request failed"
    return str(message)


def _optional_str(value: JsonValue | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: JsonValue | None) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _license_is_unavailable(license_state: str | None) -> bool:
    if license_state is None:
        return False
    normalized = license_state.lower()
    return any(token in normalized for token in UNAVAILABLE_LICENSE_TOKENS)


def _safe_stem(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return cleaned or "construct"


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
