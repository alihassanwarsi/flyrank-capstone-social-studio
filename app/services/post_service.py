from app.ingestion.url_fetcher import fetch_url_content
from app.repositories.source_post_repository import SourcePostRepository


class PostService:
    @staticmethod
    def create(*, title: str | None = None, markdown: str | None = None, url: str | None = None) -> dict:

        if markdown is not None:
            return SourcePostRepository.create(
                source_type="markdown",
                source_url=None,
                title=title,
                content=markdown,
            )

        fetched_title, content = fetch_url_content(url)

        return SourcePostRepository.create(
            source_type="url",
            source_url=url,
            title=title or fetched_title,
            content=content,
        )

    @staticmethod
    def get_by_id(post_id: int) -> dict | None:
        return SourcePostRepository.get_by_id(post_id)