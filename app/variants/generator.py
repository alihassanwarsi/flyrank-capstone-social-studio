import os

from google import genai
from dotenv import load_dotenv

from app.variants.constraints import PLATFORM_CONSTRAINTS


load_dotenv()


class VariantGenerationError(Exception):
    pass


def generate_variant(*, platform: str, source_content: str) -> str:
    profile = PLATFORM_CONSTRAINTS.get(platform)

    if profile is None:
        raise VariantGenerationError(f"Unsupported platform: {platform}")

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise VariantGenerationError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are creating a social-media variant from a stored blog post.

Platform: {platform}

Rules:
- Maximum length: {profile.max_length} characters
- Maximum hashtags: {profile.max_hashtags}
- Maximum emojis: {profile.max_emojis}

Write one platform-appropriate post.

Important:
- Use only information contained in the source post.
- Do not invent facts.
- Return only the final social post.
- Do not include explanations.

SOURCE POST:
{source_content}
""".strip()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as exc:
        raise VariantGenerationError("Gemini generation failed.") from exc

    content = response.text

    if not content or not content.strip():
        raise VariantGenerationError("Gemini returned empty content.")

    return content.strip()