import asyncio
import re
import shutil
import tempfile
from pathlib import Path

import yt_dlp

from app.config import settings
from app.models import VideoFormat, VideoInfoResponse

PLAYER_CLIENTS = [
    ["web", "mweb", "tv"],
    ["tv_embedded", "mediaconnect"],
    ["web"],
    ["mweb"],
    ["tv"],
    ["mediaconnect"],
]

COOKIES_FILE = settings.download_dir / "cookies.txt"


def _clean_url(url: str) -> str:
    url = re.sub(r"[?&]list=RD[A-Za-z0-9_-]+", "", url)
    url = re.sub(r"[?&]index=\d+", "", url)
    url = re.sub(r"[?&]si=[A-Za-z0-9_-]+", "", url)
    url = url.rstrip("?&")
    return url


def _has_cookies() -> bool:
    return COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 100


def _get_writable_cookies() -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=str(settings.download_dir))
    shutil.copy2(COOKIES_FILE, tmp.name)
    tmp.close()
    return tmp.name


def _get_opts(clients: list[str] | None = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "force_ipv4": True,
        "js_runtimes": {"node": {"cmd": ["node"]}},
        "extractor_args": {
            "youtube": {"player_client": clients or ["web"]},
            "youtubepot-bgutilscript": {"server_home": "/opt/bgutil/server"},
        },
    }
    if _has_cookies():
        opts["cookiefile"] = str(COOKIES_FILE)
    else:
        opts["http_headers"] = {
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }
    return opts


async def extract_info(url: str) -> VideoInfoResponse:
    url = _clean_url(url)

    if _has_cookies():
        cookie_path = _get_writable_cookies()
        try:
            def _extract():
                opts = _get_opts()
                opts["skip_download"] = True
                opts["cookiefile"] = cookie_path
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            info = await asyncio.to_thread(_extract)
            return _parse_formats(info)
        except Exception as e:
            if "Sign in to confirm" not in str(e):
                raise
        finally:
            Path(cookie_path).unlink(missing_ok=True)

    last_error = None
    for client_combo in PLAYER_CLIENTS:
        try:
            def _extract_fb():
                opts = _get_opts(clients=client_combo)
                opts["skip_download"] = True
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            info = await asyncio.to_thread(_extract_fb)
            return _parse_formats(info)
        except Exception as e:
            last_error = e
            if "Sign in to confirm" in str(e):
                continue
            raise

    raise last_error


def _parse_formats(info: dict) -> VideoInfoResponse:

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

    if _has_cookies():
        cookie_path = _get_writable_cookies()
        opts = _get_opts()
        opts.update({
            "format": fmt_str,
            "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
        })
        opts["cookiefile"] = cookie_path
        await _emit("extracting", percent=0)
        result_file: str = ""
        try:
            def _download():
                nonlocal result_file
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    result_file = ydl.prepare_filename(info)
                    if not result_file.endswith(".mp4"):
                        mp4 = result_file.rsplit(".", 1)[0] + ".mp4"
                        if Path(mp4).exists():
                            result_file = mp4
            await asyncio.to_thread(_download)
            return result_file
        except yt_dlp.utils.DownloadCancelled:
            await _emit("cancelled")
            raise
        except Exception as e:
            if "Sign in to confirm" not in str(e):
                await _emit("failed", error=str(e))
                raise
        finally:
            Path(cookie_path).unlink(missing_ok=True)

    last_error = None
    for client_combo in PLAYER_CLIENTS:
        opts = _get_opts(clients=client_combo)
        opts.update({
            "format": fmt_str,
            "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
        })
        await _emit("extracting", percent=0)
        result_file = ""
        try:
            def _download_fb():
                nonlocal result_file
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    result_file = ydl.prepare_filename(info)
                    if not result_file.endswith(".mp4"):
                        mp4 = result_file.rsplit(".", 1)[0] + ".mp4"
                        if Path(mp4).exists():
                            result_file = mp4
            await asyncio.to_thread(_download_fb)
            return result_file
        except yt_dlp.utils.DownloadCancelled:
            await _emit("cancelled")
            raise
        except Exception as e:
            last_error = e
            if "Sign in to confirm" in str(e):
                continue
            await _emit("failed", error=str(e))
            raise

    await _emit("failed", error=str(last_error))
    raise last_error
