from fastapi import APIRouter, HTTPException, status

from app.schemas.variant import VariantResponse, VariantUpdate
from app.services.variant_review_service import (
    VariantReviewError,
    VariantReviewService,
)
from app.services.variant_service import (
    VariantService,
    VariantServiceError,
)
from app.variants.generator import VariantGenerationError
from app.variants.validator import VariantValidationError


router = APIRouter(tags=["variants"])


@router.post("/posts/{source_post_id}/variants", response_model=list[VariantResponse], status_code=status.HTTP_201_CREATED)
def generate_variants(source_post_id: int):
    try:
        return VariantService.generate_for_post(source_post_id)

    except VariantServiceError as exc:
        if str(exc) == "Source post not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    except VariantValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors) from exc

    except VariantGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/posts/{source_post_id}/variants", response_model=list[VariantResponse])
def get_variants(source_post_id: int):
    variants = VariantService.get_for_post(source_post_id)

    if variants is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source post not found.")
    return variants


@router.patch("/variants/{variant_id}", response_model=VariantResponse)
def edit_variant(variant_id: int, payload: VariantUpdate):
    try:
        return VariantReviewService.edit(variant_id=variant_id, content=payload.content)

    except VariantReviewError as exc:
        if str(exc) == "Variant not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    except VariantValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors) from exc


@router.post("/variants/{variant_id}/approve", response_model=VariantResponse)
def approve_variant(variant_id: int):
    try:
        return VariantReviewService.approve(variant_id)

    except VariantReviewError as exc:
        if str(exc) == "Variant not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/variants/{variant_id}/reject", response_model=VariantResponse)
def reject_variant(variant_id: int):
    try:
        return VariantReviewService.reject(variant_id)

    except VariantReviewError as exc:
        if str(exc) == "Variant not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc