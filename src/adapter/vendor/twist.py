"""
module_id: adapter.vendor.twist
file: src/adapter/vendor/twist.py
task_id: T-1001
"""

from __future__ import annotations

from pathlib import Path

from adapter.vendor.base import SynthesisVendorAdapter, load_vendor_profile


class TwistVendorAdapter(SynthesisVendorAdapter):
    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> TwistVendorAdapter:
        return cls(
            load_vendor_profile(
                Path(catalogue_root) / "vendor_profiles" / "twist.yaml",
                schema_root=schema_root,
            )
        )
