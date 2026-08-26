from app.publishing.base import PublishResult, SocialPublisher


class MockXPublisher(SocialPublisher):
    def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        return PublishResult(
            success=True,
            external_post_id=f"mock-x:{idempotency_key}",
            preview=content,
        )