"""
module_id: tools.fonts
file: tools/fonts/install_canonical_fonts.py
task_id: T-201

Install bundled canonical fonts into a local font cache for renderers.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


FONT_FILES = ("Noto-Sans-Regular.ttf", "Noto-Mono-Regular.ttf")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_cache_dir() -> Path:
    return Path.home() / ".cache" / "cev-design" / "fonts"


def install_fonts(destination: Path) -> list[Path]:
    source_dir = project_root() / "fonts"
    destination.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []

    for filename in FONT_FILES:
        source = source_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing canonical font: {source}")
        target = destination / filename
        shutil.copy2(source, target)
        installed.append(target)

    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=default_cache_dir(),
        help="Font cache destination. Defaults to ~/.cache/cev-design/fonts.",
    )
    args = parser.parse_args()

    for path in install_fonts(args.dest):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
