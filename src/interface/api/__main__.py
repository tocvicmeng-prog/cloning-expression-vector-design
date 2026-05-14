"""
module_id: interface.api
file: src/interface/api/__main__.py
task_id: T-1102

API module wrapper.
"""

from __future__ import annotations

from interface.api.server import main

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)


if __name__ == "__main__":
    raise SystemExit(main())
