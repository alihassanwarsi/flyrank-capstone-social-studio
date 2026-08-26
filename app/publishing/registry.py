import os

from app.publishing.base import SocialPublisher
from app.publishing.discord import DiscordPublisher
from app.publishing.mock_linkedin import MockLinkedInPublisher
from app.publishing.mock_x import MockXPublisher

class PublisherConfigurationError(Exception):
    pass

PUBLISHERS = {
    "discord": DiscordPublisher,
    "mock_x": MockXPublisher,
    "mock_linkedin": MockLinkedInPublisher,
}

DEFAULT_ADAPTERS = {
    "discord": "discord",
    "x": "mock_x",
    "linkedin": "mock_linkedin",
}

def get_publisher_for_platform(platform: str) -> SocialPublisher:
    env_name = f"PUBLISHER_ADAPTER_{platform.upper()}"

    adapter_name = os.getenv(env_name, DEFAULT_ADAPTERS.get(platform) )

    if adapter_name is None:
        raise PublisherConfigurationError(f"No publisher configured for platform: {platform}")

    publisher_class = PUBLISHERS.get(adapter_name)

    if publisher_class is None:
        raise PublisherConfigurationError(f"Unknown publisher adapter: {adapter_name}")

    return publisher_class()