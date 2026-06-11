import asyncio
import re
from pathlib import Path

import yt_dlp

from app.config import settings
from app.models import VideoFormat, VideoInfoResponse


def _clean_url(url: str) -> str:
    url = re.sub(r"[?&]list=RD[A-Za-z0-9_-]+", "", url)
    url = re.sub(r"[?&]index=\d+", "", url)
    url = url.rstrip("?&")
    return url


def _get_base_opts() -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    cookies_path = settings.youtube_cookies_path
    if cookies_path and Path(cookies_path).exists():
        opts["cookiefile"] = cookies_path
    return opts


async def extract_info(url: str) -> VideoInfoResponse:
    url = _clean_url(url)

    def _extract():
        opts = _get_base_opts()
        opts["skip_download"] = True
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await asyncio.to_thread(_extract)

    formats: list[VideoFormat] = []
    seen = set()

    for f in info.get("formats", []):
        fid = f.get("format_id", "")
        ext = f.get("ext", "")
        height = f.get("height")
        fps = f.get("fps")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        filesize = f.get("filesize") or f.get("filesize_approx")

        has_video = vcodec != "none" and height
        has_audio = acodec != "none"

        if not has_video and not has_audio:
            continue

        if has_video and has_audio:
            label = f"{height}p (video+audio)"
            key = f"{height}p_combined"
        elif has_video:
            label = f"{height}p (video only)"
            key = f"{height}p_video_{fid}"
        else:
            abr = f.get("abr", 0)
            label = f"Audio {abr}kbps"
            key = f"audio_{fid}"

        if key in seen:
            continue
        seen.add(key)

        formats.append(VideoFormat(
            format_id=fid,
            ext=ext,
            resolution=f"{f.get('width', '?')}x{height or '?'}" if has_video else None,
            fps=fps,
            vcodec=vcodec if vcodec != "none" else None,
            acodec=acodec if acodec != "none" else None,
            filesize_approx=filesize,
            label=label,
        ))

    def _sort_key(fmt: VideoFormat) -> tuple:
        res = 0
        if fmt.resolution:
            match = re.search(r"(\d+)x(\d+)", fmt.resolution)
            if match:
                res = int(match.group(2))
        return (res, 1 if fmt.acodec else 0)

    formats.sort(key=_sort_key, reverse=True)

    return VideoInfoResponse(
        title=info.get("title", "Unknown"),
        thumbnail=info.get("thumbnail"),
        duration=info.get("duration"),
        uploader=info.get("uploader"),
        formats=formats,
    )


async def download_video(
    url: str,
    format_id: str,
    output_dir: Path,
    queue: asyncio.Queue,
    task: "Task",
) -> str:
    url = _clean_url(url)

    async def _emit(status: str, **kwargs):
        await queue.put({"status": status, **kwargs})

    def progress_hook(d):
        if task.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Task cancelled")

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else 0
            speed = d.get("speed")
            eta = d.get("eta")

            asyncio.run_coroutine_threadsafe(
                _emit("downloading", percent=percent, speed=speed, eta=eta),
                loop,
            )

        elif d["status"] == "finished":
            asyncio.run_coroutine_threadsafe(
                _emit("merging", percent=100),
                loop,
            )

    loop = asyncio.get_event_loop()

    fmt_str = f"{format_id}+bestaudio/best" if format_id != "best" else "best"

    opts = _get_base_opts()
    opts.update({
        "format": fmt_str,
        "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
    })

    await _emit("extracting", percent=0)

    result_file: str = ""

    def _download():
        nonlocal result_file
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            result_file = ydl.prepare_filename(info)
            if not result_file.endswith(".mp4"):
                mp4 = result_file.rsplit(".", 1)[0] + ".mp4"
                if Path(mp4).exists():
                    result_file = mp4

    try:
        await asyncio.to_thread(_download)
    except yt_dlp.utils.DownloadCancelled:
        await _emit("cancelled")
        raise
    except Exception as e:
        await _emit("failed", error=str(e))
        raise

    return result_file
