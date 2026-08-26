import time

from app.repositories.schedule_repository import (
    ScheduleRepository,
)
from app.services.publishing_service import (
    PublishingService,
    PublishingServiceError,
)


POLL_INTERVAL_SECONDS = 5


def process_due_schedules():
    schedules = ScheduleRepository.claim_due_schedules()

    for schedule in schedules:
        schedule_id = schedule["id"]

        print(f"Processing schedule {schedule_id}...")

        try:
            result = PublishingService.publish_schedule(schedule_id)

            print(f"Schedule {schedule_id} published "
                  f"with status {result['status']}.")

        except PublishingServiceError as exc:
            print(f"Schedule {schedule_id} failed: {exc}")


def run_worker():
    print("FlyRank Social Studio worker started.")

    while True:
        try:
            process_due_schedules()

        except Exception as exc:
            print(f"Worker cycle failed: {exc}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_worker()