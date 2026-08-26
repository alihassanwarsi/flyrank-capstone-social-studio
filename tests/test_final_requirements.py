from datetime import datetime, timedelta, timezone

import pytest

from app.publishing.mock_linkedin import MockLinkedInPublisher
from app.publishing.registry import get_publisher_for_platform
from app.services.publishing_service import PublishingService
from app.services.schedule_service import (
    ScheduleService,
    ScheduleServiceError,
)
from app.variants.validator import (
    VariantValidationError,
    validate_variant,
)


def test_bad_variant_is_blocked():
    bad_x_post = ("A" * 300) + " #one #two #three"

    with pytest.raises(VariantValidationError):
        validate_variant("x", bad_x_post)


def test_unapproved_variant_cannot_be_scheduled(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.schedule_service."
        "VariantRepository.get_by_id",
        lambda variant_id: {
            "id": variant_id,
            "status": "draft",
        },
    )

    future_time = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    with pytest.raises(
        ScheduleServiceError,
        match="Only approved variants can be scheduled",
    ):
        ScheduleService.create_schedule(
            variant_id=1,
            scheduled_for=future_time,
        )


def test_successful_publish_is_not_repeated(
    monkeypatch,
):
    existing_success = {
        "id": 50,
        "schedule_slot_id": 7,
        "adapter_name": "MockXPublisher",
        "attempt_number": 1,
        "status": "success",
        "external_post_id": "mock-123",
        "external_url": None,
        "preview": "Already published",
        "error_message": None,
    }

    monkeypatch.setattr(
        "app.services.publishing_service."
        "ScheduleRepository.get_by_id",
        lambda schedule_id: {
            "id": schedule_id,
            "variant_id": 10,
            "idempotency_key": "slot-test",
            "status": "completed",
        },
    )

    monkeypatch.setattr(
        "app.services.publishing_service."
        "PublishAttemptRepository."
        "get_successful_by_slot",
        lambda schedule_id: existing_success,
    )

    def should_never_publish(*args, **kwargs):
        raise AssertionError(
            "Publisher should not be called again."
        )

    monkeypatch.setattr(
        "app.services.publishing_service."
        "get_publisher_for_platform",
        should_never_publish,
    )

    result = PublishingService.publish_schedule(7)

    assert result == existing_success
    assert result["attempt_number"] == 1


def test_adapter_swap_is_configuration_only(
    monkeypatch,
):
    monkeypatch.setenv(
        "PUBLISHER_ADAPTER_X",
        "mock_linkedin",
    )

    publisher = get_publisher_for_platform("x")

    assert isinstance(
        publisher,
        MockLinkedInPublisher,
    )