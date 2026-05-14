"""
module_id: interface.cli
file: src/interface/cli/__main__.py
task_id: T-1101

Command-line module wrapper.
"""

from __future__ import annotations

from interface.cli.entrypoint import main

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)


if __name__ == "__main__":
    raise SystemExit(main())
