from datetime import datetime

from pydantic import BaseModel, field_validator


class MarkdownPostCreate(BaseModel):
    title: str | None = None
    markdown: str

    @field_validator("markdown")
    @classmethod
    def validate_markdown(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Markdown content cannot be empty.")

        return value


class SourcePostResponse(BaseModel):
    id: int
    source_type: str
    source_url: str | None
    title: str | None
    content: str
    created_at: datetime