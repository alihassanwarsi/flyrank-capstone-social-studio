from fastapi import APIRouter, HTTPException, status

from app.ingestion.url_fetcher import UrlFetchError
from app.schemas.post import SourcePostCreate, SourcePostResponse
from app.services.post_service import PostService


router = APIRouter(prefix="/posts", tags=["posts"],)


@router.post("", response_model=SourcePostResponse, status_code=status.HTTP_201_CREATED,)
def create_post(payload: SourcePostCreate):
    try:
        return PostService.create(
            title=payload.title,
            markdown=payload.markdown,
            url=str(payload.url) if payload.url else None,
        )

    except UrlFetchError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

@router.get("/{post_id}", response_model=SourcePostResponse,)
def get_post(post_id: int):
    post = PostService.get_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source post not found.")

    return post