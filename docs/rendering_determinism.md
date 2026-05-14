# Rendering Determinism

Canonical renderer fonts are bundled under `fonts/` and installed into a local font cache with `tools/fonts/install_canonical_fonts.py`.

`engine.design_plan` T-802 renderers follow these local rules:

- JSON output is the T-307 canonical JSON byte stream decoded as UTF-8.
- Markdown output is deterministic from ordered plan fields and contains no runtime timestamps.
- PDF output uses a fixed metadata dictionary, fixed producer string, fixed document IDs, no `/CreationDate`, and deterministic object ordering. The local no-extra renderer is byte-stable for the same plan payload.

Linux and container PDF rendering targets byte-identical output. Windows rendering targets semantic identity for future WeasyPrint-backed renderers because Pango/Cairo version skew can change byte-level output while preserving the document content, field ordering, and content hash.
