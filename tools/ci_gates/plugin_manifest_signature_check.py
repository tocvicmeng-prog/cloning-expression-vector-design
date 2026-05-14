"""
module_id: tools.ci_gates.plugin_manifest_signature_check
file: tools/ci_gates/plugin_manifest_signature_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-808
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.plugin_governance import evaluate_plugin_manifest_directory
from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate


def check_plugin_manifest_signatures(root: Path) -> GateResult:
    manifest_root = root / "catalogues" / "plugin_manifests"
    if not manifest_root.is_dir():
        return fail_gate("catalogues/plugin_manifests directory is missing")
    report = evaluate_plugin_manifest_directory(
        manifest_root,
        occurred_at_utc=datetime(2026, 5, 14, tzinfo=UTC),
    )
    if report.passed:
        return pass_gate("all plugin manifests verify against the trust keyring")
    return fail_gate(*report.messages)


def main() -> int:
    return run_gate("plugin-manifest-signature-check", check_plugin_manifest_signatures)


if __name__ == "__main__":
    raise SystemExit(main())
