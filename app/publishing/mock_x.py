from app.publishing.base import (
    PublishResult,
    SocialPublisher,
)
from app.repositories.mock_post_repository import (
    MockPostRepository,
)


class MockXPublisher(SocialPublisher):
    def publish(self, *, content: str, idempotency_key: str) -> PublishResult:
        post = MockPostRepository.create_or_get(
            adapter_name="mock_x",
            idempotency_key=idempotency_key,
            content=content,
        )

        return PublishResult(
            success=True,
            external_post_id=f"mock-x:{post['id']}",
            preview=post["content"],
        )