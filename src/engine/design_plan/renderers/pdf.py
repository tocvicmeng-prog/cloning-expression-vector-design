"""
module_id: engine.design_plan.renderers.pdf
file: src/engine/design_plan/renderers/pdf.py
task_id: T-802

Deterministic PDF renderer for design plans.
"""

from __future__ import annotations

from domain.types.design_plan import DesignRealisationPlan
from engine.design_plan.renderers.markdown import render_markdown


def render_pdf(plan: DesignRealisationPlan) -> bytes:
    lines = _wrapped_lines(render_markdown(plan), max_width=96)[:52]
    commands = ["BT", "/F1 9 Tf", "50 780 Td", "12 TL"]
    for line in lines:
        commands.append(f"({_pdf_escape(line)}) Tj")
        commands.append("T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    return _build_single_page_pdf(stream)


def _wrapped_lines(markdown: str, *, max_width: int) -> list[str]:
    result: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            result.append("")
            continue
        while len(line) > max_width:
            split_at = line.rfind(" ", 0, max_width)
            if split_at <= 0:
                split_at = max_width
            result.append(line[:split_at])
            line = line[split_at:].lstrip()
        result.append(line)
    return result


def _pdf_escape(value: str) -> str:
    encoded = value.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_single_page_pdf(stream: bytes) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        ),
        b"<< /Producer (CEV deterministic renderer) >>",
    ]
    body = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 6 0 R "
            "/ID [<4345562d44455349474e2d504c414e> <4345562d44455349474e2d504c414e>] >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(body)
