"""
module_id: domain.security.service_principals
file: src/domain/security/service_principals.py
task_id: T-313a

Engine-internal service identities used by audit append clients.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ServiceName(Enum):
    PLUGIN_GOVERNANCE = "PluginGovernance"
    ADVISORY_ACKNOWLEDGEMENT = "AdvisoryAcknowledgementService"
    SCREENING_ORCHESTRATOR = "ScreeningOrchestrator"
    AUTHORISATION_DECISION = "AuthorisationDecisionService"
    REVIEW_QUEUE = "ReviewQueueService"


@dataclass(frozen=True)
class ServicePrincipal:
    service_name: ServiceName
    token: bytes

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("service principal token cannot be empty")
