"""
module_id: tools.profile_signature_verifier
file: tools/profile_signature_verifier.py
task_id: T-314b

Standalone authorisation-profile signature verifier.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from adapter.persistence import profile_from_json
from adapter.security.profile_signing import Ed25519InstitutionalProfileVerifier
from adapter.security.signing_key_archive import SigningKeyArchiveError
from domain.types.signing_errors import ProfileVerificationResult


def verify_profile_file(
    profile_json: str | Path, key_archive: str | Path
) -> ProfileVerificationResult:
    profile = profile_from_json(Path(profile_json).read_text(encoding="utf-8"))
    return Ed25519InstitutionalProfileVerifier(key_archive).verify(profile)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a signed authorisation profile offline.")
    parser.add_argument("--profile-json", required=True, type=Path)
    parser.add_argument("--key-archive", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_profile_file(args.profile_json, args.key_archive)
    except (SigningKeyArchiveError, OSError, ValueError) as exc:
        print(
            f"profile signature verification failed before signature check: {exc}", file=sys.stderr
        )
        return 1
    if result.success:
        print("profile signature valid")
        return 0
    print(f"profile signature invalid: {result.error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
