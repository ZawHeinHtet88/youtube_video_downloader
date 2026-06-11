"""File type detection via magic bytes."""

from __future__ import annotations

from pathlib import Path

# Ordered by signature length (longest first) to avoid false matches.
MAGIC: list[tuple[bytes, str]] = [
    (b"\x00\x00\x00\x1c\x66\x74\x79\x70", ".mp4"),
    (b"\x00\x00\x00\x18\x66\x74\x79\x70", ".mp4"),
    (b"\x00\x00\x00\x20\x66\x74\x79\x70", ".mp4"),
    (b"\x89PNG\r\n\x1a\n",                  ".png"),
    (b"\xff\xd8\xff",                        ".jpg"),
    (b"\xfd7zXZ\x00",                       ".xz"),
    (b"\x1a\x45\xdf\xa3",                   ".mkv"),
    (b"\x7fELF",                             ".elf"),
    (b"\x37\x7a\xbc\xaf\x27\x1c",          ".7z"),
    (b"\x04\x22\x4d\x18",                   ".lz4"),
    (b"(\xb5\x2f\xfd",                      ".zstd"),
    (b"\x4f\x54\x54\x4f",                   ".otf"),
    (b"Rar!\x1a\x07\x00",                   ".rar"),
    (b"BZh",                                 ".bz2"),
    (b"GIF89a",                              ".gif"),
    (b"GIF87a",                              ".gif"),
    (b"ID3",                                 ".mp3"),
    (b"OggS",                                ".ogg"),
    (b"RIFF",                                ".webp"),
    (b"flac",                                ".flac"),
    (b"%PDF",                                ".pdf"),
    (b"MZ",                                  ".exe"),
    (b"\x42\x4d",                            ".bmp"),
    (b"\x1f\x8b",                            ".gz"),
    (b"\xff\xfb",                            ".mp3"),
    (b"\xff\xf3",                            ".mp3"),
    (b"\xff\xf2",                            ".mp3"),
    (b"\x49\x49\x2a\x00",                   ".tiff"),
    (b"\x4d\x4d\x00\x2a",                   ".tiff"),
    (b"\x00\x01\x00\x00\x00",               ".ttf"),
    (b"\x00\x00\x01\x00",                   ".ico"),
    (b"\xfe\xed\xfa\xcf",                   ".dylib"),
    (b"\xfe\xed\xfa\xce",                   ".dylib"),
    (b"\xca\xfe\xba\xbe",                   ".class"),
    (b"\x4c\x00\x00\x00",                   ".lnk"),
    (b"PK\x03\x04\x14\x00\x00\x00\x08\x00", ".docx"),
    (b"PK\x03\x04\x14\x00\x00\x00\x06\x00", ".xlsx"),
    (b"PK\x03\x04\x14\x00\x00\x00\x0c\x00", ".pptx"),
    (b"PK\x03\x04\x14\x00\x06\x00",         ".epub"),
    (b"PK\x03\x04",                          ".zip"),
    (b"Rar!\x1a\x07\x01\x00",               ".rar"),
]


def detect_ext(path: Path) -> str | None:
    """Read the first 16 bytes of *path* and return the matching extension, or None."""
    with open(path, "rb") as f:
        header = f.read(16)
    for sig, ext in MAGIC:
        if header[: len(sig)] == sig:
            return ext
    return None
