from fastapi import APIRouter, HTTPException, status

from app.schemas.post import MarkdownPostCreate, SourcePostResponse
from app.services.post_service import PostService


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.post(
    "",
    response_model=SourcePostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(payload: MarkdownPostCreate):
    return PostService.create_from_markdown(
        title=payload.title,
        markdown=payload.markdown,
    )


@router.get(
    "/{post_id}",
    response_model=SourcePostResponse,
)
def get_post(post_id: int):
    post = PostService.get_by_id(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source post not found.",
        )

    return post