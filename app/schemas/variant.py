from datetime import datetime

from pydantic import BaseModel


class VariantUpdate(BaseModel):
    content: str


class VariantResponse(BaseModel):
    id: int
    source_post_id: int
    platform: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime