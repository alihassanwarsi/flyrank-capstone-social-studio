from app.repositories.source_post_repository import SourcePostRepository
from app.repositories.variant_repository import VariantRepository
from app.variants.generator import generate_variant
from app.variants.validator import validate_variant


class VariantServiceError(Exception):
    pass


class VariantService:
    PLATFORMS = ("discord", "x", "linkedin")

    @staticmethod
    def generate_for_post(source_post_id: int) -> list[dict]:
        post = SourcePostRepository.get_by_id(source_post_id)

        if post is None:
            raise VariantServiceError("Source post not found.")

        existing_variants = VariantRepository.get_by_source_post(source_post_id)

        if existing_variants:
            raise VariantServiceError("Variants already exist for this source post.")

        generated_variants = []

        for platform in VariantService.PLATFORMS:
            content = generate_variant(
                platform=platform,
                source_content=post["content"],
            )

            validate_variant(platform, content)

            generated_variants.append(
                {
                    "platform": platform,
                    "content": content,
                }
            )

        saved_variants = []

        for variant in generated_variants:
            saved_variant = VariantRepository.create(
                source_post_id=source_post_id,
                platform=variant["platform"],
                content=variant["content"],
            )

            saved_variants.append(saved_variant)

        return saved_variants

    @staticmethod
    def get_for_post(source_post_id: int) -> list[dict] | None:
        post = SourcePostRepository.get_by_id(source_post_id)

        if post is None:
            return None

        return VariantRepository.get_by_source_post(source_post_id)