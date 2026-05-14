"""
module_id: tools.port_manifest_generator
file: tools/port_manifest_generator.py
task_id: T-204

Emit a seed port manifest from src/domain/ports.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]


def generate(root: Path) -> dict[str, object]:
    sys.path.insert(0, str(root / "src"))
    ports = importlib.import_module("domain.ports")

    return {
        "generated_from": "src/domain/ports",
        "canonical_port_count": len(ports.__all__),
        "ports": [{"port_name": name} for name in sorted(ports.__all__)],
    }


def main() -> int:
    print(yaml.safe_dump(generate(ROOT), sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
