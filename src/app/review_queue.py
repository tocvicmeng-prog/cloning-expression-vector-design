"""
module_id: app.review_queue
file: src/app/review_queue.py
task_id: T-315

Review-queue public API facade.
"""

from __future__ import annotations

from app.review_queue_service import (
    ReviewQueueAdminResolutionService,
    ReviewQueueResolutionResult,
    ReviewQueueService,
    ReviewQueueSubmissionResult,
)

MODULE_ID = "app.review_queue"
OWNING_TASKS = ("T-315",)

__all__ = [
    "ReviewQueueAdminResolutionService",
    "ReviewQueueResolutionResult",
    "ReviewQueueService",
    "ReviewQueueSubmissionResult",
]
