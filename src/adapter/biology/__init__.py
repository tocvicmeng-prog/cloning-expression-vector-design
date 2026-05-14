"""
module_id: adapter.biology
file: src/adapter/biology/__init__.py
task_id: T-601a..k

Biology adapter implementations and deterministic manifests.
"""

from __future__ import annotations

from adapter.biology.avoid_only import AvoidOnlyAdapter
from adapter.biology.cai import CAIAdapter
from adapter.biology.charming import CharmingAdapter
from adapter.biology.common import AdapterManifest, Payload, stable_fixture_hash
from adapter.biology.minmax import MinMaxAdapter
from adapter.biology.noderer_kozak import NodererKozakAdapter
from adapter.biology.rbs_calc_v2 import RbsCalcV2Adapter
from adapter.biology.signalp import SignalPAdapter
from adapter.biology.spliceai import SpliceAiAdapter
from adapter.biology.vienna_rna import ViennaRnaAdapter

MODULE_ID = "adapter.biology"
OWNING_TASKS = ("T-601a..k",)

BIOLOGY_ADAPTERS = (
    ViennaRnaAdapter,
    SpliceAiAdapter,
    SignalPAdapter,
    RbsCalcV2Adapter,
    NodererKozakAdapter,
    CAIAdapter,
    MinMaxAdapter,
    CharmingAdapter,
    AvoidOnlyAdapter,
)

__all__ = [
    "BIOLOGY_ADAPTERS",
    "AdapterManifest",
    "AvoidOnlyAdapter",
    "CAIAdapter",
    "CharmingAdapter",
    "MinMaxAdapter",
    "NodererKozakAdapter",
    "Payload",
    "RbsCalcV2Adapter",
    "SignalPAdapter",
    "SpliceAiAdapter",
    "ViennaRnaAdapter",
    "stable_fixture_hash",
]


def adapter_manifests() -> tuple[Payload, ...]:
    return tuple(adapter.manifest.to_payload() for adapter in BIOLOGY_ADAPTERS)
