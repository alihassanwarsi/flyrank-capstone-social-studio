from datetime import datetime

from pydantic import BaseModel


class VariantResponse(BaseModel):
    id: int
    source_post_id: int
    platform: str
    content: str
    created_at: datetime
    updated_at: datetime