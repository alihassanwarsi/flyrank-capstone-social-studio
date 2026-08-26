from datetime import datetime

from pydantic import BaseModel


class PublishAttemptResponse(BaseModel):
    id: int
    schedule_slot_id: int
    adapter_name: str
    attempt_number: int
    status: str
    external_post_id: str | None = None
    external_url: str | None = None
    preview: str | None = None
    error_message: str | None = None
    created_at: datetime