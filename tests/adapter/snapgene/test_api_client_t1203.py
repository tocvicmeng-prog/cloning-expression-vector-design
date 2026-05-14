"""
module_id: tests.adapter.snapgene.test_api_client_t1203
file: tests/adapter/snapgene/test_api_client_t1203.py
task_id: T-1203
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from adapter.io import GenBankAdapter, ImportedConstruct
from adapter.snapgene import (
    SnapGeneApiClient,
    SnapGeneApiRequestError,
    SnapGeneApiUnavailableError,
    SnapGeneCommandTransport,
    SnapGeneFileWatcher,
)
from adapter.snapgene.api_client import JsonValue
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
)

Response = Mapping[str, JsonValue]
ResponseFactory = Callable[[Mapping[str, JsonValue]], Response]


class FakeTransport:
    def __init__(self, responses: list[Response | ResponseFactory]) -> None:
        self.responses = responses
        self.requests: list[dict[str, JsonValue]] = []

    def request(self, payload: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        self.requests.append(dict(payload))
        if not self.responses:
            raise AssertionError(f"unexpected SnapGene request: {payload}")
        response = self.responses.pop(0)
        if callable(response):
            return response(payload)
        return response


def _status_response(*, license_state: str = "valid") -> Response:
    return {
        "response": "status",
        "responseCode": 0,
        "serverVersion": "7.2.1",
        "requestCount": 12,
        "lastRequest": "2026-05-14T09:00:00Z",
        "uptime": "01:22:03",
        "license": license_state,
        "licenseExpiration": "26-12-31",
        "serverIndex": 1,
    }


def _imported_construct() -> ImportedConstruct:
    record = SequenceRecord(
        id="snapgene-api-construct",
        sequence=DnaSequence("ACGTACGTACGT"),
        topology="circular",
        molecule_type=MoleculeType.DS_DNA,
    )
    feature = FeatureV14(
        role="CDS",
        qualifiers=(
            Qualifier(
                namespace="genbank",
                key="label",
                value="api-insert",
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=2, end=8, strand="+", phase="."),),
        parent_sequence_id=record.id,
    )
    return ImportedConstruct(
        construct_id=record.id,
        sequence_record=record,
        features=(feature,),
        source_format="fixture",
        source_metadata={"fixture": True},
    )


def test_status_probe_reports_live_capabilities_for_existing_server(tmp_path: Path) -> None:
    transport = FakeTransport([_status_response()])
    client = SnapGeneApiClient(transport=transport, scratch_dir=tmp_path)

    capabilities = client.capabilities()

    assert capabilities.live_api is True
    assert capabilities.file_watch_fallback is False
    assert capabilities.server_version == "7.2.1"
    assert capabilities.license_state == "valid"
    assert transport.requests == [{"request": "status"}]


def test_unconfigured_live_api_reports_file_watch_fallback(tmp_path: Path) -> None:
    fallback = SnapGeneFileWatcher(tmp_path / "watch", tmp_path / "out")
    client = SnapGeneApiClient(scratch_dir=tmp_path / "scratch", fallback_channel=fallback)

    capabilities = client.capabilities()

    assert capabilities.live_api is False
    assert capabilities.file_watch_fallback is True
    assert "not configured" in capabilities.reason


def test_sync_construct_uses_snapgene_server_import_and_export(tmp_path: Path) -> None:
    construct = _imported_construct()

    def import_response(payload: Mapping[str, JsonValue]) -> Response:
        assert payload["request"] == "importDNAFile"
        input_path = Path(str(payload["inputFile"]))
        assert input_path.read_text(encoding="utf-8").startswith("LOCUS")
        Path(str(payload["outputFile"])).write_bytes(b"synthetic snapgene server dna")
        return {"response": "importDNAFile", "responseCode": 0}

    def export_response(payload: Mapping[str, JsonValue]) -> Response:
        assert payload["request"] == "exportDNAFile"
        assert Path(str(payload["inputFile"])).suffix == ".dna"
        Path(str(payload["outputFile"])).write_bytes(GenBankAdapter().write(construct).data)
        return {"response": "exportDNAFile", "responseCode": 0}

    transport = FakeTransport(
        [
            _status_response(),
            _status_response(),
            import_response,
            _status_response(),
            export_response,
        ]
    )
    client = SnapGeneApiClient(transport=transport, scratch_dir=tmp_path / "scratch")

    result = client.sync_construct(construct)

    assert result.mode == "live_api"
    assert result.imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert result.live_import is not None
    assert result.live_import.output_dna_path.exists()
    assert [request["request"] for request in transport.requests] == [
        "status",
        "status",
        "importDNAFile",
        "status",
        "exportDNAFile",
    ]


def test_unavailable_live_api_falls_back_to_file_watch_channel(tmp_path: Path) -> None:
    construct = _imported_construct()
    transport = FakeTransport(
        [
            {
                "response": "status",
                "responseCode": 7,
                "responseMessage": "license unavailable",
            }
        ]
    )
    fallback = SnapGeneFileWatcher(tmp_path / "watch", tmp_path / "out", debounce_ms=0)
    client = SnapGeneApiClient(
        transport=transport,
        scratch_dir=tmp_path / "scratch",
        fallback_channel=fallback,
    )

    result = client.sync_construct(construct)

    assert result.mode == "file_watch_fallback"
    assert result.fallback_watch is not None
    assert result.fallback_watch.output_path.exists()
    assert "license unavailable" in (result.fallback_reason or "")


def test_nonzero_request_code_raises_structured_error(tmp_path: Path) -> None:
    construct = _imported_construct()
    transport = FakeTransport(
        [
            _status_response(),
            {
                "response": "importDNAFile",
                "responseCode": 2,
                "responseMessage": "file type unsupported",
            },
        ]
    )
    client = SnapGeneApiClient(transport=transport, scratch_dir=tmp_path)

    with pytest.raises(SnapGeneApiRequestError) as exc_info:
        client.push_construct(construct)

    assert exc_info.value.request_name == "importDNAFile"
    assert exc_info.value.response_code == 2


def test_generate_svg_map_reads_snapgene_server_output(tmp_path: Path) -> None:
    dna_path = tmp_path / "construct.dna"
    dna_path.write_bytes(b"dna")

    def svg_response(payload: Mapping[str, JsonValue]) -> Response:
        assert payload["request"] == "generateSVGMap"
        assert payload["linear"] is False
        assert payload["showFeatures"] is True
        Path(str(payload["outputSvgDom"])).write_text(
            "<svg data-sequence-length='12' />",
            encoding="utf-8",
        )
        return {"response": "generateSVGMap", "responseCode": 0}

    transport = FakeTransport([_status_response(), svg_response])
    client = SnapGeneApiClient(transport=transport, scratch_dir=tmp_path / "scratch")

    result = client.generate_svg_map(dna_path, linear=False, title="construct")

    assert result.svg_dom == "<svg data-sequence-length='12' />"
    assert result.output_svg_dom_path.exists()


def test_command_transport_serializes_request_tool_payload(tmp_path: Path) -> None:
    script = tmp_path / "snapgene_request_tool.py"
    script.write_text(
        """
import json
import sys

payload = json.loads(sys.argv[sys.argv.index("-c") + 1])
print(json.dumps({"response": payload["request"], "responseCode": 0, "serverIndex": 3}))
""".strip(),
        encoding="utf-8",
    )
    transport = SnapGeneCommandTransport((sys.executable, str(script)))

    response = transport.request({"request": "status"})

    assert response["response"] == "status"
    assert response["serverIndex"] == 3


def test_command_transport_reports_missing_request_tool() -> None:
    transport = SnapGeneCommandTransport(("definitely-not-a-snapgene-tool",))

    with pytest.raises(SnapGeneApiUnavailableError):
        transport.request({"request": "status"})
