"""Core download engine: probe, chunk, download, merge, cleanup."""

from __future__ import annotations

import math
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from downloader.config import BUFFER_SIZE, CHUNK_TIMEOUT, MAX_RETRIES, NUM_THREADS, RETRY_BACKOFF
from downloader.formatters import fmt_size, fmt_speed, log
from downloader.magic import detect_ext
from downloader.models import Chunk, DownloadState


# ── Network helpers ─────────────────────────────────────────────────────────
def probe(url: str) -> tuple[int, str]:
    """HEAD request to discover file size and filename."""
    log("[*] Sending HTTP HEAD request ...")
    r = requests.head(url, timeout=15, allow_redirects=True)
    r.raise_for_status()

    cd = r.headers.get("Content-Disposition", "")
    if "filename=" in cd:
        name = cd.split("filename=")[-1].strip("\"' ")
    else:
        name = Path(url.split("?")[0]).name or "downloaded_file"

    length = r.headers.get("Content-Length")
    if not length:
        raise RuntimeError("Server did not provide Content-Length - cannot chunk-download.")

    size = int(length)
    ranges = r.headers.get("Accept-Ranges", "")
    log(f"    File       : {name}")
    log(f"    Size       : {fmt_size(size)} ({size:,} bytes)")
    log(f"    Range OK?  : {'yes' if ranges == 'bytes' else 'unknown / no'}")
    return size, name


def build_chunks(file_size: int, num_threads: int) -> list[Chunk]:
    size = math.ceil(file_size / num_threads)
    chunks: list[Chunk] = []
    for i in range(num_threads):
        start = i * size
        end = min(start + size - 1, file_size - 1)
        if start > end:
            break
        chunks.append(Chunk(index=i, start=start, end=end, path=Path()))
    return chunks


def download_chunk(url: str, chunk: Chunk, state: DownloadState) -> None:
    log(f"[Thread {chunk.index}] Started  -> bytes {chunk.start:,}-{chunk.end:,} "
        f"({fmt_size(chunk.end - chunk.start + 1)})")

    downloaded = 0
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            range_start = chunk.start + downloaded
            headers = {
                "Range": f"bytes={range_start}-{chunk.end}",
                "Accept-Encoding": "identity",
            }
            mode = "ab" if downloaded > 0 else "wb"
            resp = requests.get(url, headers=headers, stream=True, timeout=(10, CHUNK_TIMEOUT))
            resp.raise_for_status()

            with open(chunk.path, mode) as f:
                for data in resp.iter_content(chunk_size=BUFFER_SIZE):
                    f.write(data)
                    downloaded += len(data)
                    state.update(chunk.index, downloaded)
                    sys.stdout.write(state.render_line())
                    sys.stdout.flush()

            log(f"\n[Thread {chunk.index}] Finished -> {chunk.path.name} ({fmt_size(downloaded)})")
            return

        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ReadTimeout) as exc:
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * attempt
                log(f"\n[Thread {chunk.index}] Error: {exc}")
                log(f"[Thread {chunk.index}] Retry {attempt}/{MAX_RETRIES} in {wait}s ...")
                time.sleep(wait)
            else:
                log(f"\n[Thread {chunk.index}] Failed after {MAX_RETRIES} attempts: {exc}")
                raise


# ── Merge & cleanup ─────────────────────────────────────────────────────────
def merge(chunks: list[Chunk], output: Path) -> None:
    log("\n[*] Merging chunks ...")
    with open(output, "wb") as out:
        for c in chunks:
            log(f"    Appending {c.path.name}")
            with open(c.path, "rb") as inp:
                while data := inp.read(BUFFER_SIZE):
                    out.write(data)
    log(f"[+] Final file written -> {output}")


def cleanup(chunks: list[Chunk]) -> None:
    log("[*] Cleaning up temporary chunks ...")
    for c in chunks:
        c.path.unlink(missing_ok=True)
    log("[+] Done.")


def auto_rename(path: Path) -> Path:
    """If the file has no extension, detect from magic bytes and rename."""
    if path.suffix:
        return path
    ext = detect_ext(path)
    if ext:
        new = path.with_suffix(ext)
        path.rename(new)
        log(f"[*] Detected file type: {ext} (magic bytes) -> renamed to {new.name}")
        return new
    log("[!] Could not detect file type - keeping as-is")
    return path


# ── Orchestrator ────────────────────────────────────────────────────────────
def download(url: str, output_path: Path | None = None) -> Path:
    """Download a file from *url* and return the final output path.

    If *output_path* is None the user is prompted via stdin (CLI mode).
    For GUI integration, pass *output_path* directly.
    """
    file_size, filename = probe(url)

    if output_path is None:
        user_input = input(f"    Save as [{filename}]: ").strip()
        output_path = Path(user_input) if user_input else Path(filename)

    chunks = build_chunks(file_size, NUM_THREADS)
    log(f"\n[*] Splitting into {len(chunks)} chunk(s) of ~{fmt_size(math.ceil(file_size / NUM_THREADS))} each\n")

    tmp_dir = Path(tempfile.mkdtemp(prefix="dl_"))
    for c in chunks:
        c.path = tmp_dir / f"chunk_{c.index}"

    state = DownloadState(file_size=file_size, start_time=time.perf_counter(), progress=[0] * len(chunks))

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(chunks)) as pool:
        futures = [pool.submit(download_chunk, url, c, state) for c in chunks]
        for f in as_completed(futures):
            f.result()

    elapsed = time.perf_counter() - t0
    avg_speed = file_size / elapsed if elapsed > 0 else 0
    print()
    log(f"\n[+] All chunks downloaded in {elapsed:.2f}s (avg {fmt_speed(avg_speed)})")

    merge(chunks, output_path)
    cleanup(chunks)
    output_path = auto_rename(output_path)

    size = output_path.stat().st_size
    log(f"\n{'=' * 60}")
    log(f"  COMPLETE  -  {output_path}")
    log(f"  Size      : {fmt_size(size)} ({size:,} bytes)")
    log(f"  Time      : {elapsed:.2f}s")
    log(f"  Avg Speed : {fmt_speed(avg_speed)}")
    log(f"{'=' * 60}")
    return output_path
