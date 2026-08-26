from fastapi import FastAPI

from app.api.posts import router as posts_router
from app.api.variants import router as variants_router
from app.api.schedules import router as schedules_router
from app.api.publishing import router as publishing_router

app = FastAPI(
    title="FlyRank Social Studio",
    version="0.1.0",
)

app.include_router(posts_router)
app.include_router(variants_router)
app.include_router(schedules_router)
app.include_router(publishing_router)