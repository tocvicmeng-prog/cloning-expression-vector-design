"""
module_id: tools.sop_template_signature_verifier
file: tools/sop_template_signature_verifier.py
task_id: T-316c

Standalone SOP-template signature verifier.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from adapter.security.signing_key_archive import SigningKeyArchiveError
from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateVerifier,
    sop_template_from_json,
)
from domain.types.signing_errors import SopTemplateVerificationResult


def verify_sop_template_file(
    template_json: str | Path,
    key_archive: str | Path,
) -> SopTemplateVerificationResult:
    template = sop_template_from_json(Path(template_json).read_text(encoding="utf-8"))
    return Ed25519InstitutionalSopTemplateVerifier(key_archive).verify(template)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a signed SOP template offline.")
    parser.add_argument("--template-json", required=True, type=Path)
    parser.add_argument("--key-archive", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_sop_template_file(args.template_json, args.key_archive)
    except (SigningKeyArchiveError, OSError, ValueError) as exc:
        print(
            f"SOP-template signature verification failed before signature check: {exc}",
            file=sys.stderr,
        )
        return 1
    if result.success:
        print("SOP-template signature valid")
        return 0
    print(f"SOP-template signature invalid: {result.error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
