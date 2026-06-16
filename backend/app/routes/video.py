from fastapi import APIRouter, HTTPException

from app.models import (
    VideoInfoRequest,
    VideoInfoResponse,
    CookieRequest,
    CookieStatus,
)
from app.services.ytdlp import extract_info
from app.config import settings

router = APIRouter()

COOKIES_FILE = settings.download_dir / "cookies.txt"


@router.get("/health")
async def health():
    import yt_dlp
    return {
        "status": "ok",
        "ytdlp_version": yt_dlp.version.__version__,
    }


@router.get("/api/cookies", response_model=CookieStatus)
async def get_cookie_status():
    exists = COOKIES_FILE.exists()
    return CookieStatus(
        has_cookies=exists,
        size_bytes=COOKIES_FILE.stat().st_size if exists else 0,
    )


@router.post("/api/cookies", response_model=CookieStatus)
async def set_cookies(req: CookieRequest):
    content = req.cookies.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Cookies content is empty")

    if not content.startswith("# Netscape"):
        raise HTTPException(status_code=400, detail="Invalid cookie format. Must be Netscape HTTP Cookie File format exported from browser extension.")

    COOKIES_FILE.write_text(content, encoding="utf-8")

    return CookieStatus(
        has_cookies=True,
        size_bytes=COOKIES_FILE.stat().st_size,
    )


@router.post("/api/video/info", response_model=VideoInfoResponse)
async def video_info(req: VideoInfoRequest):
    try:
        return await extract_info(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
