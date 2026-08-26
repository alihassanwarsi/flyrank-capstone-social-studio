from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PublishResult:
    success: bool
    external_post_id: str | None = None
    external_url: str | None = None
    preview: str | None = None


class SocialPublisher(ABC):
    @abstractmethod
    def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        pass