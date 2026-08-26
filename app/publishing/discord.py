import os

import httpx
from dotenv import load_dotenv

from app.publishing.base import PublishResult, SocialPublisher


load_dotenv()

class DiscordPublisherError(Exception):
    pass

class DiscordPublisher(SocialPublisher):
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

        if not self.webhook_url:
            raise DiscordPublisherError("DISCORD_WEBHOOK_URL is not configured.")

    def publish(self, *, content: str, idempotency_key: str) -> PublishResult:
        try:
            response = httpx.post(
                self.webhook_url,
                params={"wait": "true"},
                json={
                    "content": content,
                },
                timeout=10.0,
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise DiscordPublisherError("Discord publishing failed.") from exc

        data = response.json()

        message_id = data.get("id")
        channel_id = data.get("channel_id")
        guild_id = data.get("guild_id")

        external_url = None

        if message_id and channel_id and guild_id:
            external_url = (
                f"https://discord.com/channels/"
                f"{guild_id}/{channel_id}/{message_id}"
            )

        return PublishResult(
            success=True,
            external_post_id=message_id,
            external_url=external_url,
            preview=content,
        )