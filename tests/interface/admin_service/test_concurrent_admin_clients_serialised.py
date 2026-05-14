"""
module_id: tests.interface.admin_service.test_concurrent_admin_clients_serialised
file: tests/interface/admin_service/test_concurrent_admin_clients_serialised.py
task_id: T-1103b
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from domain.types.admin_ipc import (
    AdminIpcRequest,
    AdminIpcResponse,
    AdminIpcStatus,
    AdminServiceVerb,
)
from tests.interface.admin_service.helpers import NOW, harness, token


def test_concurrent_admin_clients_serialised() -> None:
    active = 0
    max_active = 0
    order: list[str] = []

    def handler(_principal: object, request: AdminIpcRequest) -> dict[str, object]:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        order.append(str(request.request_id))
        time.sleep(0.01)
        active -= 1
        return {"request_id": str(request.request_id)}

    app = harness(handlers={AdminServiceVerb.LIST_PROFILES: handler})

    def call(index: int) -> AdminIpcResponse:
        return app.client.list_profiles(
            token(),
            {"index": index},
            request_id=f"req-{index}",
            requested_at_utc=NOW,
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        responses = tuple(pool.map(call, range(10)))

    assert all(response.status is AdminIpcStatus.ACCEPTED for response in responses)
    assert max_active == 1
    assert sorted(order) == [f"req-{index}" for index in range(10)]
