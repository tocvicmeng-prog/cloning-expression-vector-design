"""
module_id: tools.ci
file: tools/ci/run_pytest.py
task_id: T-201

Run pytest while allowing the T-201 zero-test bootstrap state.
"""

from __future__ import annotations

import subprocess
import sys

PYTEST_NO_TESTS_EXIT_CODE = 5


def main(argv: list[str]) -> int:
    result = subprocess.run([sys.executable, "-m", "pytest", *argv], check=False)
    if result.returncode == PYTEST_NO_TESTS_EXIT_CODE:
        print("pytest collected no tests; allowed during T-201 bootstrap")
        return 0
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
