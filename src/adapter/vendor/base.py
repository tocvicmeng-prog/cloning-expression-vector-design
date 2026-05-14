"""
module_id: adapter.vendor.base
file: src/adapter/vendor/base.py
task_id: T-1001

Shared static synthesis-vendor feasibility implementation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Literal, cast

from adapter.catalogue import load_catalogue, schema_for_catalogue
from domain.sequence import DnaSequence, Sha256, sha256_text

VendorFeasibilityStatus = Literal["accepted", "warning", "rejected"]


class VendorRejectionClass(Enum):
    LENGTH_UNDER_MIN = "length_under_min"
    LENGTH_OVERFLOW = "length_overflow"
    GC_EXTREME = "gc_extreme"
    REPEAT_EXCESS = "repeat_excess"
    ADAPTER_COLLISION = "adapter_collision"
    PRODUCT_FORMAT_MISMATCH = "product_format_mismatch"
    HOMOPOLYMER_EXCESS = "homopolymer_excess"


@dataclass(frozen=True)
class VendorFeasibilityRequest:
    request_id: str
    sequence: DnaSequence
    product_type: str
    service_id: str | None = None
    delivery_format: str | None = None
    cloning_option: str | None = None
    adapters: tuple[str, ...] = ()
    session_id: str | None = None
    construct_id: str | None = None
    construct_checksum: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.product_type:
            raise ValueError("product_type cannot be empty")
        for adapter in self.adapters:
            DnaSequence(adapter)


@dataclass(frozen=True)
class VendorFeasibilityIssue:
    rejection_class: VendorRejectionClass
    severity: Literal["warning", "rejection"]
    message: str
    service_id: str

    def __post_init__(self) -> None:
        if not self.message:
            raise ValueError("vendor feasibility issue message cannot be empty")
        if not self.service_id:
            raise ValueError("service_id cannot be empty")


@dataclass(frozen=True)
class VendorFeasibilityReport:
    vendor_id: str
    request_id: str
    service_id: str
    status: VendorFeasibilityStatus
    sequence_length_bp: int
    global_gc_pct: Decimal
    issues: tuple[VendorFeasibilityIssue, ...]
    profile_version: str
    profile_content_hash: Sha256
    session_id: str | None = None
    construct_id: str | None = None
    construct_checksum: str | None = None

    def __post_init__(self) -> None:
        if not self.vendor_id:
            raise ValueError("vendor_id cannot be empty")
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.service_id:
            raise ValueError("service_id cannot be empty")
        has_rejection = any(issue.severity == "rejection" for issue in self.issues)
        if self.status == "rejected" and not has_rejection:
            raise ValueError("rejected vendor reports require a rejection issue")
        if self.status != "rejected" and has_rejection:
            raise ValueError("vendor reports with rejection issues must be rejected")

    @property
    def rejected(self) -> bool:
        return self.status == "rejected"

    @property
    def rejection_classes(self) -> frozenset[VendorRejectionClass]:
        return frozenset(
            issue.rejection_class for issue in self.issues if issue.severity == "rejection"
        )


@dataclass(frozen=True)
class AutoPartitionResult:
    vendor_id: str
    service_id: str
    fragments: tuple[DnaSequence, ...]
    feasible: bool
    reason: str


@dataclass(frozen=True)
class VendorCostEstimate:
    vendor_id: str
    service_id: str
    currency: str
    quote_date_utc: date
    amount: Decimal | None
    pricing_tier: str
    quote_required: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class VendorServiceProfile:
    service_id: str
    name: str
    delivery_format: str
    min_bp: int
    max_bp: int
    service_tier: str
    quote_required_over_bp: int | None
    constraints: Mapping[str, object]

    def __post_init__(self) -> None:
        if self.min_bp <= 0 or self.max_bp <= 0:
            raise ValueError("vendor service length bounds must be positive")
        if self.min_bp > self.max_bp:
            raise ValueError("vendor service min_bp cannot exceed max_bp")


@dataclass(frozen=True)
class VendorProfile:
    vendor_id: str
    name: str
    profile_version: str
    default_currency: str
    services: tuple[VendorServiceProfile, ...]
    profile_content_hash: Sha256

    def __post_init__(self) -> None:
        if not self.vendor_id:
            raise ValueError("vendor_id cannot be empty")
        service_ids = tuple(service.service_id for service in self.services)
        if len(set(service_ids)) != len(service_ids):
            raise ValueError("vendor service IDs must be unique")

    def service_for_request(self, request: VendorFeasibilityRequest) -> VendorServiceProfile:
        if request.service_id is not None:
            for service in self.services:
                if service.service_id == request.service_id:
                    return service
            raise ValueError(f"unknown service_id for {self.vendor_id}: {request.service_id}")

        product_key = request.product_type.lower()
        for service in self.services:
            haystack = f"{service.service_id} {service.name} {service.service_tier}".lower()
            if product_key in haystack:
                return service
        return self.services[0]


class SynthesisVendorAdapter:
    def __init__(self, profile: VendorProfile) -> None:
        self.profile = profile

    @property
    def vendor_id(self) -> str:
        return self.profile.vendor_id

    @classmethod
    def from_catalogue(
        cls,
        profile_path: str | Path,
        *,
        schema_root: str | Path,
    ) -> SynthesisVendorAdapter:
        return cls(load_vendor_profile(profile_path, schema_root=schema_root))

    def check(self, request: VendorFeasibilityRequest) -> VendorFeasibilityReport:
        service = self.profile.service_for_request(request)
        issues = _sequence_issues(request, service)
        status: VendorFeasibilityStatus = (
            "rejected"
            if any(issue.severity == "rejection" for issue in issues)
            else "warning"
            if issues
            else "accepted"
        )
        return VendorFeasibilityReport(
            vendor_id=self.vendor_id,
            request_id=request.request_id,
            service_id=service.service_id,
            status=status,
            sequence_length_bp=len(request.sequence),
            global_gc_pct=_gc_percent(request.sequence.body),
            issues=issues,
            profile_version=self.profile.profile_version,
            profile_content_hash=self.profile.profile_content_hash,
            session_id=request.session_id,
            construct_id=request.construct_id,
            construct_checksum=request.construct_checksum,
        )

    def auto_partition(self, request: VendorFeasibilityRequest) -> AutoPartitionResult:
        service = self.profile.service_for_request(request)
        body = request.sequence.body
        if len(body) <= service.max_bp:
            return AutoPartitionResult(
                vendor_id=self.vendor_id,
                service_id=service.service_id,
                fragments=(request.sequence,),
                feasible=len(body) >= service.min_bp,
                reason="single fragment is within vendor service bounds",
            )

        chunks = tuple(
            DnaSequence(body[index : index + service.max_bp])
            for index in range(0, len(body), service.max_bp)
        )
        feasible = all(len(chunk) >= service.min_bp for chunk in chunks)
        return AutoPartitionResult(
            vendor_id=self.vendor_id,
            service_id=service.service_id,
            fragments=chunks,
            feasible=feasible,
            reason=(
                "partitioned into vendor-orderable fragments"
                if feasible
                else "partition leaves a terminal fragment below vendor minimum length"
            ),
        )

    def estimate_cost(
        self,
        *,
        product_type: str,
        scale: int,
        cloning_option: str | None,
        currency: str,
        quote_date_utc: date,
    ) -> VendorCostEstimate:
        request = VendorFeasibilityRequest(
            request_id="cost-estimate",
            sequence=DnaSequence("A" * max(scale, 1)),
            product_type=product_type,
            cloning_option=cloning_option,
        )
        service = self.profile.service_for_request(request)
        quote_required = (
            service.quote_required_over_bp is not None and scale > service.quote_required_over_bp
        )
        amount = None if quote_required else _deterministic_amount(service, scale)
        notes = (
            ("platform produces a human-submission file; direct ordering is disabled",)
            if quote_required
            else ()
        )
        return VendorCostEstimate(
            vendor_id=self.vendor_id,
            service_id=service.service_id,
            currency=currency or self.profile.default_currency,
            quote_date_utc=quote_date_utc,
            amount=amount,
            pricing_tier=service.service_tier,
            quote_required=quote_required,
            notes=notes,
        )


def load_vendor_profile(profile_path: str | Path, *, schema_root: str | Path) -> VendorProfile:
    path = Path(profile_path)
    document = load_catalogue(path, schema_for_catalogue(path, schema_root))
    payload = document.payload
    services_raw = _expect_list(payload["services"], "services")
    services = tuple(_parse_service(item) for item in services_raw)
    return VendorProfile(
        vendor_id=_expect_str(payload, "vendor_id"),
        name=_expect_str(payload, "name"),
        profile_version=_expect_str(payload, "profile_version"),
        default_currency=str(payload.get("default_currency", "USD")),
        services=services,
        profile_content_hash=sha256_text(path.read_text(encoding="utf-8")),
    )


def _parse_service(raw: object) -> VendorServiceProfile:
    data = _expect_mapping(raw, "service")
    return VendorServiceProfile(
        service_id=_expect_str(data, "id"),
        name=_expect_str(data, "name"),
        delivery_format=_expect_str(data, "delivery_format"),
        min_bp=_expect_int(data, "min_bp"),
        max_bp=_expect_int(data, "max_bp"),
        service_tier=str(data.get("service_tier", "standard")),
        quote_required_over_bp=_optional_int(data.get("quote_required_over_bp")),
        constraints=_expect_mapping(data["sequence_constraints"], "sequence_constraints"),
    )


def _sequence_issues(
    request: VendorFeasibilityRequest,
    service: VendorServiceProfile,
) -> tuple[VendorFeasibilityIssue, ...]:
    body = request.sequence.body
    issues: list[VendorFeasibilityIssue] = []
    if len(body) < service.min_bp:
        issues.append(
            _issue(
                VendorRejectionClass.LENGTH_UNDER_MIN,
                f"sequence length {len(body)} bp is below {service.min_bp} bp minimum",
                service,
            )
        )
    if len(body) > service.max_bp:
        issues.append(
            _issue(
                VendorRejectionClass.LENGTH_OVERFLOW,
                f"sequence length {len(body)} bp exceeds {service.max_bp} bp maximum",
                service,
            )
        )
    gc_pct = _gc_percent(body)
    gc_min = _constraint_decimal(service, "global_gc_min_pct")
    gc_max = _constraint_decimal(service, "global_gc_max_pct")
    if gc_pct < gc_min or gc_pct > gc_max:
        issues.append(
            _issue(
                VendorRejectionClass.GC_EXTREME,
                f"global GC {gc_pct}% outside vendor bounds {gc_min}-{gc_max}%",
                service,
            )
        )
    repeat_block_bp = _constraint_int(service, "direct_repeat_block_bp")
    if _has_direct_repeat(body, repeat_block_bp):
        issues.append(
            _issue(
                VendorRejectionClass.REPEAT_EXCESS,
                f"direct repeat at or above {repeat_block_bp} bp detected",
                service,
            )
        )
    for adapter in request.adapters:
        if adapter.upper() and adapter.upper() in body:
            issues.append(
                _issue(
                    VendorRejectionClass.ADAPTER_COLLISION,
                    "requested adapter sequence already appears in the insert",
                    service,
                )
            )
            break
    if request.delivery_format and not _delivery_format_matches(
        requested=request.delivery_format,
        offered=service.delivery_format,
    ):
        issues.append(
            _issue(
                VendorRejectionClass.PRODUCT_FORMAT_MISMATCH,
                (
                    f"requested delivery format {request.delivery_format!r} is incompatible "
                    f"with {service.delivery_format!r}"
                ),
                service,
            )
        )
    return tuple(issues)


def _issue(
    rejection_class: VendorRejectionClass,
    message: str,
    service: VendorServiceProfile,
) -> VendorFeasibilityIssue:
    return VendorFeasibilityIssue(
        rejection_class=rejection_class,
        severity="rejection",
        message=message,
        service_id=service.service_id,
    )


def _gc_percent(sequence: DnaSequence | str) -> Decimal:
    body = sequence.body if isinstance(sequence, DnaSequence) else sequence
    gc_count = body.count("G") + body.count("C")
    return (Decimal(gc_count) * Decimal(100) / Decimal(len(body))).quantize(Decimal("0.01"))


def _has_direct_repeat(sequence: str, repeat_bp: int) -> bool:
    if repeat_bp <= 0 or len(sequence) < repeat_bp * 2:
        return False
    seen: set[str] = set()
    for index in range(0, len(sequence) - repeat_bp + 1):
        kmer = sequence[index : index + repeat_bp]
        if kmer in seen:
            return True
        seen.add(kmer)
    return False


def _delivery_format_matches(*, requested: str, offered: str) -> bool:
    if requested == offered:
        return True
    return requested in offered.split("_or_")


def _deterministic_amount(service: VendorServiceProfile, scale: int) -> Decimal:
    tier_multiplier = {
        "standard": Decimal("0.09"),
        "standard_fragment": Decimal("0.08"),
        "hifi_fragment": Decimal("0.11"),
        "rapid": Decimal("0.13"),
        "clonal": Decimal("0.16"),
        "long_or_complex": Decimal("0.20"),
    }.get(service.service_tier, Decimal("0.10"))
    return (Decimal(max(scale, service.min_bp)) * tier_multiplier).quantize(Decimal("0.01"))


def _constraint_int(service: VendorServiceProfile, key: str) -> int:
    value = service.constraints.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{service.service_id} constraint {key} must be an integer")
    return value


def _constraint_decimal(service: VendorServiceProfile, key: str) -> Decimal:
    value = service.constraints.get(key)
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ValueError(f"{service.service_id} constraint {key} must be numeric")
    return Decimal(str(value))


def _expect_mapping(raw: object, name: str) -> Mapping[str, object]:
    if not isinstance(raw, dict):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], raw)


def _expect_list(raw: object, name: str) -> list[object]:
    if not isinstance(raw, list):
        raise ValueError(f"{name} must be a list")
    return raw


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _expect_int(data: Mapping[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("optional integer field must be an integer")
    return value
