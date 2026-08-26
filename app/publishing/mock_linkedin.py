from app.publishing.base import PublishResult, SocialPublisher


class MockLinkedInPublisher(SocialPublisher):
    def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        return PublishResult(
            success=True,
            external_post_id=f"mock-linkedin:{idempotency_key}",
            preview=content,
        )