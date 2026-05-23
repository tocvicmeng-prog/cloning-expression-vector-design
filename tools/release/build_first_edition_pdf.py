"""
module_id:           tools.release.build_first_edition_pdf
file:                tools/release/build_first_edition_pdf.py
task_id:             T-FIRST-EDITION

Build the First Edition user-guide PDF from its Markdown source.

Reads `docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.md`
and emits the same content as a paginated PDF, in two locations:

1. `docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf`
   — the repo-side distribution copy (committed to git for release artefact).

2. `ui/public/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf`
   — the UI-side copy. Vite copies `public/*` verbatim into the build, so the
   React app can link to `/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf`
   directly. The upper-right "User Guide" icon in `ui/src/App.tsx` points here.

PDF engine: `markdown-pdf` (fpdf2-backed; pure Python, no GTK / Cairo /
wkhtmltopdf required). Mermaid diagrams in the Markdown render as fenced
code blocks in the PDF (text-preserving); the Markdown version renders
diagrams natively in any modern Markdown viewer.

Usage:
    python -m tools.release.build_first_edition_pdf
    python -m tools.release.build_first_edition_pdf --md path/to/source.md
    python -m tools.release.build_first_edition_pdf --no-ui-copy

Exit codes:
    0   PDF generated successfully (both copies on disk)
    1   Markdown source missing
    2   PDF generation failed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_MD_RELATIVE = (
    "docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.md"
)
DEFAULT_PDF_RELATIVE = (
    "docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf"
)
UI_PUBLIC_RELATIVE = (
    "ui/public/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf"
)


def _repo_root() -> Path:
    """Walk upward from this file to locate the repo root (contains README.md + pyproject.toml)."""
    here = Path(__file__).resolve()
    for ancestor in [here, *here.parents]:
        if (ancestor / "pyproject.toml").is_file() and (ancestor / "README.md").is_file():
            return ancestor
    raise RuntimeError("repo root not found from tools/release/build_first_edition_pdf.py")


def build_pdf(md_path: Path, pdf_path: Path) -> int:
    """Convert md_path → pdf_path. Returns number of bytes written."""
    try:
        from markdown_pdf import MarkdownPdf, Section  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "markdown-pdf is required. Install with:\n"
            "    pip install --user markdown-pdf\n"
            f"(import failed: {exc})"
        ) from exc

    md_text = md_path.read_text(encoding="utf-8")
    pdf = MarkdownPdf(toc_level=3)
    # Single section preserves overall heading hierarchy for the table of contents.
    pdf.add_section(Section(md_text, toc=True))
    pdf.meta["title"] = "Cloning & Expression Vector Design Toolkit — First Edition"
    pdf.meta["author"] = "General Molecular Expression Service Pty Ltd (GMExpression®, GMES)"
    pdf.meta["subject"] = (
        "User guide for designing, validating, and preparing expression vectors "
        "for wet-lab execution. For Research Use Only."
    )
    pdf.meta["keywords"] = (
        "cloning, expression vector, plasmid, GMExpression, GMES, "
        "molecular biology, vector design, junior researcher, first edition"
    )
    pdf.save(pdf_path)
    return pdf_path.stat().st_size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--md",
        type=Path,
        default=None,
        help=f"Markdown source path (default: {DEFAULT_MD_RELATIVE} relative to repo root)",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help=f"PDF output path (default: {DEFAULT_PDF_RELATIVE} relative to repo root)",
    )
    parser.add_argument(
        "--no-ui-copy",
        action="store_true",
        help="Skip copying the PDF to ui/public/ (default: copy)",
    )
    args = parser.parse_args(argv)

    root = _repo_root()
    md_path = args.md if args.md else (root / DEFAULT_MD_RELATIVE)
    pdf_path = args.pdf if args.pdf else (root / DEFAULT_PDF_RELATIVE)

    if not md_path.is_file():
        sys.stderr.write(
            f"build_first_edition_pdf: source Markdown not found: "
            f"{md_path.relative_to(root) if md_path.is_absolute() else md_path}\n"
        )
        return 1

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        size_bytes = build_pdf(md_path, pdf_path)
    except SystemExit as exc:
        sys.stderr.write(f"build_first_edition_pdf: {exc}\n")
        return 2
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"build_first_edition_pdf: PDF generation failed: {exc}\n")
        return 2

    sys.stderr.write(
        f"build_first_edition_pdf: wrote {pdf_path.relative_to(root)} "
        f"({size_bytes:,} bytes)\n"
    )

    if not args.no_ui_copy:
        ui_path = root / UI_PUBLIC_RELATIVE
        ui_path.parent.mkdir(parents=True, exist_ok=True)
        ui_path.write_bytes(pdf_path.read_bytes())
        sys.stderr.write(
            f"build_first_edition_pdf: also wrote {ui_path.relative_to(root)} "
            f"({size_bytes:,} bytes) for Vite to serve from /\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
