"""Multi-threaded file downloader with parallel chunk-based fetching."""

from downloader.config import BUFFER_SIZE, NUM_THREADS, PROGRESS_BAR_LEN
from downloader.formatters import fmt_eta, fmt_size, fmt_speed, log
from downloader.magic import MAGIC, detect_ext
from downloader.models import Chunk, DownloadState
from downloader.downloader import (
    auto_rename,
    build_chunks,
    cleanup,
    download_chunk,
    download,
    merge,
    probe,
)
from downloader.youtube import (
    download_yt,
    is_video_url,
    list_formats,
    probe_yt,
)

__all__ = [
    # config
    "BUFFER_SIZE",
    "NUM_THREADS",
    "PROGRESS_BAR_LEN",
    # formatters
    "fmt_eta",
    "fmt_size",
    "fmt_speed",
    "log",
    # magic
    "MAGIC",
    "detect_ext",
    # models
    "Chunk",
    "DownloadState",
    # downloader
    "auto_rename",
    "build_chunks",
    "cleanup",
    "download_chunk",
    "download",
    "merge",
    "probe",
    # youtube
    "download_yt",
    "is_video_url",
    "list_formats",
    "probe_yt",
]
