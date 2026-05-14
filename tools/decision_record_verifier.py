"""
module_id: tools.decision_record_verifier
file: tools/decision_record_verifier.py
task_id: T-314b

Standalone decision-record signature verifier.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from adapter.security.decision_record_signing import (
    PerPrincipalDecisionRecordVerifier,
    signed_decision_from_json,
)
from adapter.security.signing_key_archive import SigningKeyArchiveError
from domain.types.signing_errors import DecisionRecordVerificationResult


def verify_decision_record_file(
    signed_record_json: str | Path,
    key_archive: str | Path,
) -> DecisionRecordVerificationResult:
    signed = signed_decision_from_json(Path(signed_record_json).read_text(encoding="utf-8"))
    return PerPrincipalDecisionRecordVerifier(key_archive).verify(signed)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a signed decision record offline.")
    parser.add_argument("--signed-record-json", required=True, type=Path)
    parser.add_argument("--key-archive", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_decision_record_file(args.signed_record_json, args.key_archive)
    except (SigningKeyArchiveError, OSError, ValueError) as exc:
        print(
            f"decision-record signature verification failed before signature check: {exc}",
            file=sys.stderr,
        )
        return 1
    if result.success:
        print("decision-record signature valid")
        return 0
    print(f"decision-record signature invalid: {result.error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
