from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json

from app.models import (
    VideoInfoRequest,
    VideoInfoResponse,
    DownloadRequest,
    DownloadTaskResponse,
    TaskInfo,
    ProgressData,
)
from app.services.ytdlp import extract_info, download_video
from app.services.task_manager import task_manager
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


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

    from pathlib import Path
    filepath = Path(task.filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    import re
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
