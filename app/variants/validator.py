import re

from app.variants.constraints import PLATFORM_CONSTRAINTS


HASHTAG_PATTERN = re.compile(r"(?<!\w)#\w+")

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "]"
)


class VariantValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_variant(platform: str, content: str) -> None:
    if platform not in PLATFORM_CONSTRAINTS:
        raise VariantValidationError(
            [f"Unsupported platform: {platform}"]
        )

    profile = PLATFORM_CONSTRAINTS[platform]
    errors = []

    if not content.strip():
        errors.append("Content cannot be empty.")

    if len(content) > profile.max_length:
        errors.append(
            f"Content exceeds {profile.max_length} characters."
        )

    hashtag_count = len(HASHTAG_PATTERN.findall(content))

    if hashtag_count > profile.max_hashtags:
        errors.append(
            f"Too many hashtags. Maximum is {profile.max_hashtags}."
        )

    emoji_count = len(EMOJI_PATTERN.findall(content))

    if emoji_count > profile.max_emojis:
        errors.append(
            f"Too many emojis. Maximum is {profile.max_emojis}."
        )

    if (
        profile.max_exclamations is not None
        and content.count("!") > profile.max_exclamations
    ):
        errors.append(
            f"Too many exclamation marks. "
            f"Maximum is {profile.max_exclamations}."
        )

    if profile.reject_excessive_caps:
        letters = [char for char in content if char.isalpha()]

        if len(letters) >= 20:
            uppercase_count = sum(
                1 for char in letters if char.isupper()
            )

            uppercase_ratio = uppercase_count / len(letters)

            if uppercase_ratio > 0.6:
                errors.append("Excessive all-caps text is not allowed.")

    lowered_content = content.lower()

    for term in profile.forbidden_terms:
        if re.search(rf"\b{re.escape(term)}\b", lowered_content):
            errors.append(
                f"Tone rule violated by casual term: '{term}'."
            )

    if errors:
        raise VariantValidationError(errors)