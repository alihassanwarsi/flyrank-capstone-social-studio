from app.repositories.variant_repository import VariantRepository
from app.variants.validator import validate_variant


class VariantReviewError(Exception):
    pass

class VariantReviewService:
    @staticmethod
    def edit(*, variant_id: int, content: str) -> dict:
        variant = VariantRepository.get_by_id(variant_id)

        if variant is None:
            raise VariantReviewError("Variant not found.")

        if variant["status"] != "draft":
            raise VariantReviewError("Only draft variants can be edited.")

        validate_variant(
            variant["platform"],
            content,
        )

        return VariantRepository.update_content(
            variant_id=variant_id,
            content=content,
        )

    @staticmethod
    def approve(variant_id: int) -> dict:
        variant = VariantRepository.get_by_id(variant_id)

        if variant is None:
            raise VariantReviewError("Variant not found.")

        if variant["status"] != "draft":
            raise VariantReviewError("Only draft variants can be approved.")

        return VariantRepository.update_status(variant_id=variant_id, status="approved")

    @staticmethod
    def reject(variant_id: int) -> dict:
        variant = VariantRepository.get_by_id(variant_id)

        if variant is None:
            raise VariantReviewError("Variant not found.")

        if variant["status"] != "draft":
            raise VariantReviewError("Only draft variants can be rejected.")

        return VariantRepository.update_status(variant_id=variant_id, status="rejected")