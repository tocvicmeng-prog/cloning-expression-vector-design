"""
module_id: adapter.vendor
file: src/adapter/vendor/__init__.py
task_id: T-1001

Static synthesis-vendor adapters.
"""

from __future__ import annotations

from adapter.vendor.base import (
    AutoPartitionResult,
    SynthesisVendorAdapter,
    VendorCostEstimate,
    VendorFeasibilityIssue,
    VendorFeasibilityReport,
    VendorFeasibilityRequest,
    VendorProfile,
    VendorRejectionClass,
    VendorServiceProfile,
    load_vendor_profile,
)
from adapter.vendor.genscript import GenScriptVendorAdapter
from adapter.vendor.idt import IdtVendorAdapter
from adapter.vendor.twist import TwistVendorAdapter

__all__ = [
    "AutoPartitionResult",
    "GenScriptVendorAdapter",
    "IdtVendorAdapter",
    "SynthesisVendorAdapter",
    "TwistVendorAdapter",
    "VendorCostEstimate",
    "VendorFeasibilityIssue",
    "VendorFeasibilityReport",
    "VendorFeasibilityRequest",
    "VendorProfile",
    "VendorRejectionClass",
    "VendorServiceProfile",
    "load_vendor_profile",
]
