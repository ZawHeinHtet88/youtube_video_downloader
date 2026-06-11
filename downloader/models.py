"""Data classes for download state and chunk tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from downloader.config import PROGRESS_BAR_LEN
from downloader.formatters import fmt_eta, fmt_size, fmt_speed


@dataclass
class Chunk:
    index: int
    start: int
    end: int
    path: Path


@dataclass
class DownloadState:
    """Thread-safe shared state for progress tracking."""

    file_size: int
    start_time: float
    progress: list[int] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def update(self, thread_idx: int, bytes_downloaded: int) -> None:
        with self.lock:
            self.progress[thread_idx] = bytes_downloaded

    def snapshot(self) -> tuple[int, float, float]:
        """Return (total_done, speed, eta) — lock-free read for rendering."""
        with self.lock:
            total = sum(self.progress)
        elapsed = time.perf_counter() - self.start_time
        speed = total / elapsed if elapsed > 0 else 0
        eta = (self.file_size - total) / speed if speed > 0 else 0
        return total, speed, eta

    def render_line(self) -> str:
        total, speed, eta = self.snapshot()
        filled = int(PROGRESS_BAR_LEN * total / self.file_size)
        bar = "#" * filled + "-" * (PROGRESS_BAR_LEN - filled)
        return (
            f"\r  |{bar}| {total / self.file_size * 100:6.2f}%  "
            f"{fmt_size(total)}/{fmt_size(self.file_size)}  "
            f"{fmt_speed(speed)}  ETA {fmt_eta(eta)}"
        )
