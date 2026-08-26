from fastapi import APIRouter, HTTPException, status

from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.services.schedule_service import (
    ScheduleService,
    ScheduleServiceError,
)


router = APIRouter(tags=["schedules"])

@router.post("/variants/{variant_id}/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def schedule_variant(variant_id: int, payload: ScheduleCreate):
    try:
        return ScheduleService.create_schedule(variant_id=variant_id, scheduled_for=payload.scheduled_for)

    except ScheduleServiceError as exc:
        if str(exc) == "Variant not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc