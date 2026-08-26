from datetime import datetime

from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.variant_repository import VariantRepository


class ScheduleServiceError(Exception):
    pass

class ScheduleService:
    @staticmethod
    def create_schedule(*, variant_id: int, scheduled_for: datetime) -> dict:
        variant = VariantRepository.get_by_id(variant_id)

        if variant is None:
            raise ScheduleServiceError("Variant not found.")

        if variant["status"] != "approved":
            raise ScheduleServiceError("Only approved variants can be scheduled.")

        if scheduled_for <= datetime.now(scheduled_for.tzinfo):
            raise ScheduleServiceError("Scheduled time must be in the future.")

        return ScheduleRepository.create(variant_id=variant_id, scheduled_for=scheduled_for)