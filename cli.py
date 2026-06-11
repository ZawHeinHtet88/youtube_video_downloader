#!/usr/bin/env python3
"""CLI entry point for the multi-threaded downloader."""

import sys
from pathlib import Path

from downloader import download, download_yt, is_video_url, list_formats, log, probe_yt


def main() -> None:
    print("=" * 50)
    print("  Multi-Threaded CLI Downloader")
    print("=" * 50)
    url = input("Enter download URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    try:
        if is_video_url(url):
            handle_video(url)
        else:
            download(url)
    except Exception as exc:
        log(f"\n[!] Error: {exc}")
        sys.exit(1)


def handle_video(url: str) -> None:
    """Handle YouTube / video site downloads."""
    print()
    print("  Video site detected!")
    print("  1) Download best quality (MP4)")
    print("  2) Choose format manually")
    print("  3) Cancel")
    choice = input("  Select [1]: ").strip() or "1"

    if choice == "2":
        list_formats(url)
        fmt = input("\n  Enter format ID (or 'best'): ").strip() or "best"
        if fmt == "best":
            fmt_spec = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            fmt_spec = f"{fmt}+bestaudio/best"
        output = input("  Save as [video.mp4]: ").strip()
        out_path = Path(output) if output else None
        download_yt(url, output_path=out_path, format_spec=fmt_spec)
    elif choice == "3":
        print("  Cancelled.")
    else:
        output = input("  Save as [video.mp4]: ").strip()
        out_path = Path(output) if output else None
        download_yt(url, output_path=out_path)


if __name__ == "__main__":
    main()
