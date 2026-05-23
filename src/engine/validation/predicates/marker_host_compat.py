"""
module_id:           engine.validation.predicates.marker_host_compat
file:                src/engine/validation/predicates/marker_host_compat.py
task_id:             audit-fix-H4

MR-59 marker ↔ host auxotrophic compatibility predicate.

Background — collaborative audit (2026-05-23) found that v0.2 shipped MR-55,
MR-59, MR-60 declared as `severity: HARD` in REQUIREMENTS.md § 11.6 but
implemented as `Severity.INFO` stubs. v0.2.1 audit fix H4 promotes ONE of
them (MR-59 — marker-host auxotrophic compatibility) to a real predicate as
a demonstration of the MarkersResolver wiring (audit fix C3) and the yeast
genotype token work (audit fix C5).

MR-55 (methylation-aware enzyme planning) and MR-60 (Y2H marker compatibility)
remain `Severity.INFO` stubs at v0.2.1 — they each require additional supporting
data structures (REBASE methylation-sensitivity table for MR-55; Y2H-specific
strain catalogue extension for MR-60) that are properly v0.3 scope.

The MR-59 semantic
-----------------

A yeast auxotrophic marker (URA3, LEU2, HIS3, TRP1, MET15, LYS2) PROVIDES a
selection signal IFF the chosen host has the corresponding chromosomal locus
DELETED or DISRUPTED. The MarkersResolver returns the marker's
`host_genotype_requirement` field (e.g., `"ura3-Δ (e.g., BY4741, BY4742, INVSc1)"`).
The host's `genotype` field carries the canonical Brachmann-1998 / Sikorski-Hieter-1989
genotype string (post-audit-fix C5: `"MATa his3Δ1 leu2Δ0 met15Δ0 ura3Δ0 ..."`).

The predicate compares the required-genotype token(s) against the host genotype
string. If absent, the marker provides no selection and the construct WILL NOT
SELECT in transformation — this is a HARD fire-the-rule condition.

Implementation note
-------------------

The MarkersResolver may be `None` (v0.1.0 baseline behaviour) — in that case
the predicate returns `Severity.INFO` (the v0.2 stub semantic) because it
cannot resolve the marker payload. A future Phase 5/6 enforcement-gate run
should require a resolver be wired.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.validation_context import ValidationContext

# Patterns extracted from the marker's `host_genotype_requirement` field that we
# look for in the host's `genotype` string. Each marker requires ANY of its
# acceptable tokens to be present.
_GENOTYPE_TOKEN_PATTERN = re.compile(
    r"(?:^|\s|/|\(|,)(ura3-Δ\d*|ura3Δ\d*|ura3-52|"
    r"leu2-Δ\d*|leu2Δ\d*|leu2-3,112|leu2-3|leu2|"
    r"his3-Δ\d*|his3Δ\d*|his3-200|his3-11,15|his3|"
    r"trp1-Δ\d*|trp1Δ\d*|trp1-289|trp1-901|trp1-1|trp1|"
    r"met15-Δ\d*|met15Δ\d*|met-|"
    r"lys2-Δ\d*|lys2Δ\d*|lys2-801|lys2-128|"
    r"ade2-1|ade2-101|ade2)",
    re.IGNORECASE,
)


def _extract_required_locus(host_genotype_requirement: str) -> str:
    """Extract the locus name (URA3, LEU2, etc.) from the requirement string.

    The requirement strings look like `"ura3-Δ (e.g., BY4741, ...)"` — we want
    the leading lowercase locus name to match against the host genotype.
    """
    if not host_genotype_requirement:
        return ""
    # Pull first parenthesised-deletion token (e.g., "ura3-Δ" from "ura3-Δ (e.g., BY4741)")
    match = re.match(r"\s*([A-Za-z0-9]+)(?:-Δ|Δ|-\d+,?\d*)", host_genotype_requirement)
    if match:
        return match.group(1).lower()
    # Fall back to first lowercase word
    fallback = re.match(r"\s*([a-z][a-z0-9]+)", host_genotype_requirement.lower())
    return fallback.group(1) if fallback else ""


def _host_genotype_includes_locus(host_genotype: str, required_locus: str) -> bool:
    """Return True if the host genotype contains a deletion/disruption marker for the locus."""
    if not required_locus or not host_genotype:
        return False
    locus = required_locus.lower()
    # Match any of: "ura3-Δ0", "ura3Δ0", "ura3-52", "ura3" (with deletion-like context),
    # using the canonical genotype tokens in the post-fix-C5 host strings.
    tokens = _GENOTYPE_TOKEN_PATTERN.findall(host_genotype)
    return any(token.lower().startswith(locus) for token in tokens)


def mr_59_marker_host_genotype_compat(context: ValidationContext, rule: ValidationRule) -> Severity:
    """MR-59: auxotrophic marker selection requires complementary host genotype.

    Returns `rule.severity` (HARD) if a yeast auxotrophic marker in the
    construct's marker list cannot be selected against the chosen host
    because the host has the corresponding locus intact.

    Returns `Severity.INFO` if:
    - no markers_resolver wired (v0.1.0 baseline behaviour)
    - the construct doesn't declare a marker or a host
    - the marker isn't a yeast auxotrophic marker
    - the marker has no host_genotype_requirement field
    - the host genotype field is empty or placeholder

    These "missing data → INFO" outcomes are deliberate: an absent precondition
    is not a violation, only an opportunity for human curator review.
    """
    resolver = context.markers_resolver
    if resolver is None:
        return Severity.INFO

    payload = context.design_payload
    construct_markers = payload.get("markers", ())
    host = payload.get("host", {})
    if not isinstance(construct_markers, list | tuple):
        return Severity.INFO
    if not isinstance(host, Mapping):
        return Severity.INFO
    host_genotype = str(host.get("genotype", ""))
    if not host_genotype or "verify" in host_genotype.lower():
        return Severity.INFO

    for marker_ref in construct_markers:
        marker_id = (
            str(marker_ref)
            if isinstance(marker_ref, str)
            else str(marker_ref.get("id", "") if isinstance(marker_ref, Mapping) else "")
        )
        if not marker_id:
            continue
        marker_payload = resolver.resolve(marker_id)
        if marker_payload is None:
            continue
        required = str(marker_payload.get("host_genotype_requirement", ""))
        if not required:
            continue
        required_locus = _extract_required_locus(required)
        if not required_locus:
            continue
        if not _host_genotype_includes_locus(host_genotype, required_locus):
            # Auxotrophic marker fired but host has the locus intact — no selection.
            return rule.severity

    return Severity.INFO


MARKER_HOST_COMPAT_PREDICATES = {
    "mr_59": mr_59_marker_host_genotype_compat,
}


__all__ = [
    "MARKER_HOST_COMPAT_PREDICATES",
    "mr_59_marker_host_genotype_compat",
]
