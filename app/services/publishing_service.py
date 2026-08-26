from app.publishing.registry import get_publisher_for_platform
from app.repositories.publish_attempt_repository import (
    PublishAttemptRepository,
)
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.variant_repository import VariantRepository


class PublishingServiceError(Exception):
    pass

class PublishingService:
    @staticmethod
    def publish_schedule(schedule_id: int) -> dict:
        schedule = ScheduleRepository.get_by_id(schedule_id)

        if schedule is None:
            raise PublishingServiceError("Schedule slot not found.")

        existing_success = PublishAttemptRepository.get_successful_by_slot(schedule_id)
    
        if existing_success is not None:
            return existing_success

        variant = VariantRepository.get_by_id(schedule["variant_id"])

        if variant is None:
            raise PublishingServiceError("Variant not found.")

        if variant["status"] != "approved":
            raise PublishingServiceError("Only approved variants can be published.")

        publisher = get_publisher_for_platform(variant["platform"])

        adapter_name = publisher.__class__.__name__

        attempt = PublishAttemptRepository.create_started(schedule_slot_id=schedule_id, adapter_name=adapter_name)

        ScheduleRepository.update_status(schedule_id=schedule_id, status="processing")

        try:
            result = publisher.publish(content=variant["content"], idempotency_key=schedule["idempotency_key"])

            if not result.success:
                raise PublishingServiceError("Publisher returned an unsuccessful result.")

            successful_attempt = (
                PublishAttemptRepository.mark_success(
                    attempt_id=attempt["id"],
                    external_post_id=result.external_post_id,
                    external_url=result.external_url,
                    preview=result.preview,
                )
            )

            ScheduleRepository.update_status(schedule_id=schedule_id, status="completed")

            VariantRepository.update_status(variant_id=variant["id"], status="published")

            return successful_attempt

        except Exception as exc:
            PublishAttemptRepository.mark_failed(attempt_id=attempt["id"], error_message=str(exc))

            ScheduleRepository.update_status(schedule_id=schedule_id, status="failed")

            raise PublishingServiceError("Publishing failed.") from exc