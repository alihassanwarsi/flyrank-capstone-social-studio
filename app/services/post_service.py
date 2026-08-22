from app.repositories.source_post_repository import SourcePostRepository


class PostService:
    @staticmethod
    def create_from_markdown(
        *,
        markdown: str,
        title: str | None = None,
    ) -> dict:
        return SourcePostRepository.create(
            source_type="markdown",
            source_url=None,
            title=title,
            content=markdown,
        )

    @staticmethod
    def get_by_id(post_id: int) -> dict | None:
        return SourcePostRepository.get_by_id(post_id)