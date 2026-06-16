from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json
import re
from pathlib import Path

from app.models import (
    VideoInfoRequest,
    VideoInfoResponse,
    DownloadRequest,
    DownloadTaskResponse,
    TaskInfo,
    ProgressData,
    CookieRequest,
    CookieStatus,
)
from app.services.ytdlp import extract_info, download_video
from app.services.task_manager import task_manager
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


@router.get("/api/debug")
async def debug():
    import yt_dlp
    import subprocess

    result = {
        "ytdlp_version": yt_dlp.version.__version__,
        "node_available": False,
    }

    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        result["node_available"] = True
        result["node_version"] = r.stdout.strip()
    except Exception as e:
        result["node_error"] = str(e)

    try:
        from pathlib import Path
        result["pot_server_exists"] = Path("/opt/bgutil/server/build/main.js").exists()
    except Exception as e:
        result["pot_check_error"] = str(e)

    # Test 1: Without cookies - verbose
    try:
        import io
        import logging

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        yt_dlp_logger = logging.getLogger("yt_dlp")
        yt_dlp_logger.addHandler(handler)
        yt_dlp_logger.setLevel(logging.DEBUG)

        opts = {
            "no_warnings": True,
            "skip_download": True,
            "force_ipv4": True,
            "logger": yt_dlp_logger,
            "extractor_args": {
                "youtube": {"player_client": ["web"]},
                "youtubepot-bgutilscript": {"server_home": "/opt/bgutil/server"},
            },
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=nwVmxz44c1Y", download=False)
        result["test_no_cookies"] = f"SUCCESS: {info.get('title', '')[:50]}"
        result["yt_dlp_log"] = log_capture.getvalue()[-1000:]
    except Exception as e:
        err = str(e)
        result["test_no_cookies_error"] = err[:300]
        result["yt_dlp_log"] = log_capture.getvalue()[-1000:] if 'log_capture' in dir() else ""

    # Test 2: With cookies
    from app.services.ytdlp import COOKIES_FILE, _get_writable_cookies
    if COOKIES_FILE.exists():
        try:
            cookie_path = _get_writable_cookies()
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "force_ipv4": True,
                "cookiefile": cookie_path,
                "extractor_args": {
                    "youtube": {"player_client": ["web"]},
                    "youtubepot-bgutilscript": {"server_home": "/opt/bgutil/server"},
                },
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info("https://www.youtube.com/watch?v=nwVmxz44c1Y", download=False)
            result["test_with_cookies"] = f"SUCCESS: {info.get('title', '')[:50]}"
        except Exception as e:
            err = str(e)
            result["test_with_cookies_error"] = err[:300]
        finally:
            Path(cookie_path).unlink(missing_ok=True)

    return result


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


@router.post("/api/download", response_model=DownloadTaskResponse)
async def start_download(req: DownloadRequest):
    task = task_manager.create(req.url)

    async def _run():
        try:
            filepath = await download_video(
                url=req.url,
                format_id=req.format_id,
                output_dir=settings.download_dir,
                queue=task.queue,
                task=task,
            )
            task.filename = filepath
            task.status = "completed"
            await task.queue.put({"status": "completed", "filename": filepath})
        except asyncio.CancelledError:
            task.status = "cancelled"
        except Exception as e:
            task.status = "failed"
            await task.queue.put({"status": "failed", "error": str(e)})

    task.status = "downloading"
    task._task = asyncio.create_task(_run())

    return DownloadTaskResponse(task_id=task.task_id)


@router.get("/api/download/{task_id}/progress")
async def download_progress(task_id: str):
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_stream():
        while True:
            try:
                msg = await asyncio.wait_for(task.queue.get(), timeout=300)
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'status': 'timeout'})}\n\n"
                break

            yield f"data: {json.dumps(msg)}\n\n"

            if msg.get("status") in ("completed", "failed", "cancelled", "timeout"):
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/api/download/{task_id}/file")
async def download_file(task_id: str):
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "completed" or not task.filename:
        raise HTTPException(status_code=400, detail="File not ready")

    filepath = Path(task.filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filepath.name)

    return FileResponse(
        path=str(filepath),
        filename=safe_name,
        media_type="application/octet-stream",
    )


@router.get("/api/tasks")
async def list_tasks():
    return [
        TaskInfo(
            task_id=t.task_id,
            url=t.url,
            status=t.status,
            filename=t.filename,
            created_at=t.created_at,
        )
        for t in task_manager.list_all()
    ]


@router.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_manager.cancel(task_id):
        return {"status": "cancelled"}

    raise HTTPException(status_code=400, detail="Cannot cancel task")
