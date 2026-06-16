import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.video import router as video_router

log = logging.getLogger("idm")

app = FastAPI(
    title="Internet Download Manager API",
    version="1.0.0",
    description="YouTube video download backend powered by yt-dlp",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_router)


@app.on_event("startup")
def on_startup():
    import yt_dlp
    log.info("yt-dlp version: %s", yt_dlp.version.__version__)
    log.info("Cookies file: %s", settings.download_dir / "cookies.txt")

    from app.services.ytdlp import start_pot_server
    start_pot_server()


@app.on_event("shutdown")
def on_shutdown():
    from app.services.ytdlp import stop_pot_server
    stop_pot_server()
