# Rendering Determinism

Canonical renderer fonts are bundled under `fonts/` and installed into a local font cache with `tools/fonts/install_canonical_fonts.py`.

Linux and container PDF rendering targets byte-identical output once PDF rendering lands. Windows rendering targets semantic identity because Pango/Cairo version skew can change byte-level output while preserving the document content, field ordering, and content hash.
