from datetime import datetime

from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    scheduled_for: datetime


class ScheduleResponse(BaseModel):
    id: int
    variant_id: int
    scheduled_for: datetime
    status: str
    created_at: datetime