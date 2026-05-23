# Install Guide — Cloning & Expression Vector Design Toolkit v0.2.1

This document is the **zip-package install guide** for the v0.2.1 release.
It is bundled inside `cev-toolkit-v0.2.1-install.zip` (the release asset on
GitHub) and is also valid for cloning the repo from git.

Owner: **General Molecular Expression Service Pty Ltd (GMExpression®, GMES)**
License: GPL-3.0-only
Released: 2026-05-23

---

## 0. What you get when you unzip

```
cev-toolkit-v0.2.1/
├── README.md                          ← project overview
├── INSTALL.md                         ← this file
├── LICENSE                            ← GPL-3.0-only
├── IP_POLICY.md                       ← counsel-facing IP posture
├── pyproject.toml                     ← Python project metadata
├── uv.lock                            ← deterministic dep lockfile
├── ARCHITECTURE.md                    ← binding architecture (~ 2.7k lines)
├── REQUIREMENTS.md                    ← functional + safety requirements
├── CODING_AGENDA.md                   ← implementation plan (~ 3k lines)
├── TASK_BOARD.md                      ← live status dashboard
├── ROADMAP.md                         ← phase-level record
├── Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md   ← KB v2.0
├── Cloning_Expression_Vector_Design_White_Paper.md               ← White Paper
├── src/                               ← Python source (domain / engine /
│                                         adapter / app / interface)
├── ui/
│   ├── dist/                          ← pre-built React UI (ready to serve)
│   ├── public/                        ← static assets incl. First Edition PDF
│   ├── package.json                   ← UI deps manifest (for re-build only)
│   ├── index.html
│   ├── vite.config.ts
│   └── tsconfig*.json
├── catalogues/                        ← hosts / markers / rules YAML
├── schemas/                           ← JSON Schemas
├── tools/                             ← CI gates + release helpers
├── tests/                             ← unit + integration + UAT tests
├── docs/
│   ├── instructions/
│   │   ├── Cloning_Expression_Vector_Design_Toolkit_First_Edition.md   ← user guide
│   │   └── Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf  ← user guide (PDF)
│   ├── release/                       ← release notes (v0.1.0, v0.2.0, v0.2.1)
│   ├── handover/                      ← cadence trail + audit reports
│   ├── ml_corpus/                     ← 148-record ML training corpus
│   ├── fork-readiness/                ← operational checklist for commercial fork
│   ├── port_manifest.yaml             ← 51 canonical ports
│   ├── task_manifest.yaml             ← 92 active task cards
│   └── traceability_index.md          ← 621 file-header traceability entries
├── LICENSES/
│   └── THIRD_PARTY_NOTICES.md         ← SnapGene + Addgene nominative-use
├── dist/                              ← pre-built Python distribution
│   ├── cloning_expression_vector_design-0.2.1-py3-none-any.whl
│   └── cloning_expression_vector_design-0.2.1.tar.gz
├── tasks/                             ← per-card task briefs
└── .pre-commit-config.yaml            ← pre-commit hooks incl. credential-scan
```

---

## 1. System requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 11 x64 / macOS 12+ / Linux glibc 2.31+ | Windows 11 x64 |
| Python | 3.11.15+ (strictly &lt; 3.12) | 3.11.15 |
| `uv` package manager | 0.5+ | 0.11.14 |
| Node.js (only if re-building UI) | 20+ | 20 LTS |
| Disk | 4 GB free | 8 GB free |
| RAM | 4 GB | 8 GB+ |
| Git (only if updating in place) | 2.40+ | latest |

Optional:
- Microsoft Edge / Chrome / Firefox (to open the pre-built UI from `ui/dist/`)
- A modern Markdown viewer (e.g., Obsidian, VS Code) for the bundled docs

---

## 2. Quick install (recommended path)

### 2.1 Install the Python package from the bundled wheel

This is the fastest path if you just want the Python engine + CLI.

```bash
# from inside the unzipped cev-toolkit-v0.2.1/ directory
python -m pip install --upgrade pip
python -m pip install ./dist/cloning_expression_vector_design-0.2.1-py3-none-any.whl
```

This installs the runtime + core dependencies. Optional extras must be added
explicitly:

```bash
# add I/O extras (Biopython + SBOL3 + SnapGene index reader)
python -m pip install "./dist/cloning_expression_vector_design-0.2.1-py3-none-any.whl[io,sbol3,biology-genbank]"

# add CLI / API / PDF extras
python -m pip install "./dist/cloning_expression_vector_design-0.2.1-py3-none-any.whl[cli,api,pdf]"
```

### 2.2 Serve the UI from the bundled `ui/dist/`

No Node install required for the pre-built UI. Any static file server works:

```bash
# Python built-in (development only; no production hardening)
python -m http.server 8080 --directory ui/dist

# now open http://127.0.0.1:8080/ in your browser
```

The upper-right **book icon** in the nav opens the bundled First Edition PDF.

### 2.3 Read the First Edition user guide

The user guide is in TWO places (identical content):

- `docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.md`
  (Markdown — renders Mermaid diagrams in modern viewers)
- `docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf`
  (PDF — 6.1 MB, ~ 4365 lines / ~ 150 pages of content)

The UI link goes to `ui/public/...First_Edition.pdf` (same file, served at
`/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf` from the
running UI).

---

## 3. Developer / contributor install (full source)

If you need the full development workflow (running tests, modifying source,
re-building wheels), use `uv` against the source tree:

### 3.1 Windows (PowerShell)

```powershell
cd cev-toolkit-v0.2.1
python -m pip install "uv==0.11.14"
python -m uv sync --frozen --no-editable --group dev --extra io
$env:PYTHONPATH = 'src;.'
.\.venv\Scripts\python.exe tools\agenda_consistency_check.py
.\.venv\Scripts\python.exe -m pytest tests/ -m "not slow"
```

### 3.2 Linux / macOS (bash)

```bash
cd cev-toolkit-v0.2.1
python -m pip install "uv==0.11.14"
python -m uv sync --frozen --no-editable --group dev --extra io
export PYTHONPATH=src:.
.venv/bin/python tools/agenda_consistency_check.py
.venv/bin/python -m pytest tests/ -m "not slow"
```

### 3.3 Re-building the UI from source

```bash
cd ui
npm install
npm run build
# output: ui/dist/ (overwrites the bundled pre-built UI)
npm test -- --run
```

### 3.4 Re-generating the First Edition PDF

```bash
# from the project root, with the venv active
python -m tools.release.build_first_edition_pdf
# writes docs/instructions/...pdf + ui/public/...pdf
```

---

## 4. First-run verification

After install, confirm everything is green:

```bash
# from the project root
python tools/agenda_consistency_check.py
# → "agenda consistency check passed: 92 active task headings, 51 canonical ports"

# import-linter (requires the [dev] extras)
.venv/Scripts/lint-imports.exe --config .importlinter
# → "Contracts: 4 kept, 0 broken."

# Critical CI gates
python -m tools.ci_gates.audit_traceability_check
python -m tools.ci_gates.credential_scan_check
python -m tools.ci_gates.doc_numeric_consistency_check
python -m tools.ci_gates.ml_corpus_license_check
# → all exit 0
```

---

## 5. Reproducing the "680 passed" release-notes test figure

The default install gives you 645 passing tests. To reach the release-notes
"680 passed" figure, install the optional SBOL3 + Biopython extras:

```bash
python -m uv sync --extra io --extra sbol3 --extra biology-genbank
.venv/Scripts/python.exe -m pytest tests/
```

This is documented in `docs/release/v0.2.0_release_notes.md` "Prerequisites"
section (added in v0.2.1 audit-fix M2 — release notes
reproducibility documentation).

---

## 6. Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'sbol3'` | Optional SBOL3 extra not installed | `python -m pip install "...whl[sbol3]"` or `uv sync --extra sbol3` |
| `ModuleNotFoundError: No module named 'adapter'` | PYTHONPATH not set | `export PYTHONPATH=src:.` (or PowerShell equivalent) |
| `UnicodeEncodeError: charmap` on Windows | Trying to print non-ASCII paths via cp1252 stdout | Set `PYTHONIOENCODING=utf-8`; never print absolute Path objects |
| UI build errors after edit | Cached node_modules | `rm -rf ui/node_modules ui/package-lock.json && cd ui && npm install` |
| `agenda_consistency_check.py FAILED` after edit | task_manifest.yaml drift | Re-run; if persistent, check `EXPECTED_TOTAL` constants in the checker |

For more troubleshooting, see Appendix J in the First Edition user guide.

---

## 7. Disclaimer + licensing

- **For Research Use Only (RUO).** Not certified for clinical, diagnostic,
  or therapeutic purposes.
- License: **GPL-3.0-only** (see `LICENSE`)
- Trademark: **GMExpression®** is a registered trademark of General Molecular
  Expression Service Pty Ltd.
- Third-party trademarks (SnapGene®, Addgene®, etc.) used under nominative-use
  fair-use principles; see `LICENSES/THIRD_PARTY_NOTICES.md`.
- For any commercial fork: consult the Fork-Readiness Memorandum
  (`ARCHITECTURE.md § 9.6` and the operational checklist at
  `docs/fork-readiness/checklist.md`) and engage counsel before release.

---

© 2026 General Molecular Expression Service Pty Ltd (GMExpression®, GMES).
All rights reserved.
