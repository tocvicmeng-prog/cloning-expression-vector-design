"""
module_id: adapter.vendor.genscript
file: src/adapter/vendor/genscript.py
task_id: T-1001
"""

from __future__ import annotations

from pathlib import Path

from adapter.vendor.base import SynthesisVendorAdapter, load_vendor_profile


class GenScriptVendorAdapter(SynthesisVendorAdapter):
    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> GenScriptVendorAdapter:
        return cls(
            load_vendor_profile(
                Path(catalogue_root) / "vendor_profiles" / "genscript.yaml",
                schema_root=schema_root,
            )
        )
