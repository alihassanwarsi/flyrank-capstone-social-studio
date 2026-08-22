from datetime import datetime

from pydantic import BaseModel, HttpUrl, model_validator


class SourcePostCreate(BaseModel):
    title: str | None = None
    markdown: str | None = None
    url: HttpUrl | None = None

    @model_validator(mode="after")
    def validate_source(self):
        if self.markdown is not None and not self.markdown.strip():
            raise ValueError("Markdown content cannot be empty.")

        if (self.markdown is None) == (self.url is None):
            raise ValueError("Provide exactly one of markdown or url.")

        return self


class SourcePostResponse(BaseModel):
    id: int
    source_type: str
    source_url: str | None
    title: str | None
    content: str
    created_at: datetime