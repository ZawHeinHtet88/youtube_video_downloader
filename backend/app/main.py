import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.video import router as video_router

log = logging.getLogger("idm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import yt_dlp
    log.info("yt-dlp version: %s", yt_dlp.version.__version__)
    log.info("Cookies file: %s", settings.download_dir / "cookies.txt")
    yield


app = FastAPI(
    title="Internet Download Manager API",
    version="1.0.0",
    description="YouTube video download backend powered by yt-dlp",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_router)
