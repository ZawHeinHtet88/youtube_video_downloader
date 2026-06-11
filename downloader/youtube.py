"""YouTube / video site downloader wrapping yt-dlp."""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from downloader.formatters import fmt_eta, fmt_size, fmt_speed, log

_YTDL_EXTRAS = "youtube.com,youtu.be,vimeo.com,facebook.com,x.com,twitter.com,tiktok.com,dailymotion.com"


def _clean_youtube_url(url: str) -> str:
    """Remove playlist/mix params that confuse yt-dlp."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("list", None)
    params.pop("index", None)
    clean_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=clean_query))


def is_video_url(url: str) -> bool:
    """Return True if the URL looks like a supported video site."""
    patterns = [
        r"youtube\.com",
        r"youtu\.be",
        r"vimeo\.com",
        r"facebook\.com/.+/videos",
        r"fb\.watch",
        r"x\.com/.+/video",
        r"twitter\.com/.+/video",
        r"tiktok\.com",
        r"dailymotion\.com",
    ]
    return any(re.search(p, url) for p in patterns)


def _progress_hook(d: dict) -> None:
    """yt-dlp progress hook — renders a progress bar in the terminal."""
    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes", 0)
        speed = d.get("speed") or 0
        eta = d.get("eta") or 0

        if total > 0:
            pct = downloaded / total * 100
            bar_len = 40
            filled = int(bar_len * downloaded / total)
            bar = "#" * filled + "-" * (bar_len - filled)
            sys.stdout.write(
                f"\r  |{bar}| {pct:6.2f}%  "
                f"{fmt_size(downloaded)}/{fmt_size(total)}  "
                f"{fmt_speed(speed)}  ETA {fmt_eta(eta)}"
            )
            sys.stdout.flush()

    elif d["status"] == "finished":
        total = d.get("total_bytes") or d.get("downloaded_bytes") or 0
        print(f"\n  Download complete: {fmt_size(total)}")


def probe_yt(url: str) -> dict:
    """Extract video metadata without downloading (title, formats, thumbnail)."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp[default]")

    url = _clean_youtube_url(url)
    log("[*] Fetching video info ...")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title", "Unknown")
    duration = info.get("duration") or 0
    formats = info.get("formats", [])

    log(f"    Title      : {title}")
    log(f"    Duration   : {fmt_eta(duration)}")
    log(f"    Formats    : {len(formats)} available")

    return info


def download_yt(
    url: str,
    output_path: Path | None = None,
    format_spec: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
) -> Path:
    """Download a video from YouTube or other supported sites.

    Args:
        url: Video URL.
        output_path: Directory or file path. If None, uses current directory.
        format_spec: yt-dlp format selector string.

    Returns:
        Path to the downloaded file.
    """
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp[default]")

    url = _clean_youtube_url(url)

    # Determine output template
    if output_path and output_path.suffix:
        outtmpl = str(output_path)
    elif output_path:
        outtmpl = str(output_path.with_suffix(".mp4"))
    else:
        outtmpl = "%(title)s.%(ext)s"

    ydl_opts = {
        "format": format_spec,
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "progress_hooks": [_progress_hook],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    log("[*] Starting download ...")
    t0 = time.perf_counter()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    elapsed = time.perf_counter() - t0

    # yt-dlp may merge into .mp4
    final = Path(filename)
    mp4_version = final.with_suffix(".mp4")
    if mp4_version.exists():
        final = mp4_version

    size = final.stat().st_size if final.exists() else 0
    speed = size / elapsed if elapsed > 0 else 0

    print()
    log(f"\n{'=' * 60}")
    log(f"  COMPLETE  -  {final}")
    log(f"  Title     : {info.get('title', 'Unknown')}")
    log(f"  Size      : {fmt_size(size)}")
    log(f"  Time      : {elapsed:.2f}s")
    log(f"  Speed     : {fmt_speed(speed)}")
    log(f"{'=' * 60}")

    return final


def list_formats(url: str) -> None:
    """Print available formats for a video URL."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp[default]")

    url = _clean_youtube_url(url)
    log("[*] Fetching available formats ...")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    log(f"\n  Title: {info.get('title', 'Unknown')}")
    log(f"  Duration: {fmt_eta(info.get('duration') or 0)}\n")

    log(f"  {'ID':<12} {'Ext':<6} {'Resolution':<12} {'Size':<12} {'Note'}")
    log(f"  {'-'*60}")

    for f in info.get("formats", []):
        fid = f.get("format_id", "?")
        ext = f.get("ext", "?")
        res = f.get("resolution", "audio only")
        size = fmt_size(f.get("filesize") or f.get("filesize_approx") or 0)
        note = f.get("format_note", "")
        log(f"  {fid:<12} {ext:<6} {res:<12} {size:<12} {note}")
