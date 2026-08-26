from fastapi import APIRouter, HTTPException, status

from app.schemas.publish import PublishAttemptResponse
from app.services.publishing_service import (
    PublishingService,
    PublishingServiceError,
)

router = APIRouter(tags=["publishing"])

@router.post("/schedules/{schedule_id}/publish", response_model=PublishAttemptResponse)
def publish_schedule(schedule_id: int):
    try:
        return PublishingService.publish_schedule(schedule_id)

    except PublishingServiceError as exc:
        if str(exc) == "Schedule slot not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc