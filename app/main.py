from fastapi import FastAPI

from app.api.posts import router as posts_router


app = FastAPI(
    title="FlyRank Social Studio",
    version="0.1.0",
)

app.include_router(posts_router)