from __future__ import annotations

import re
from dataclasses import dataclass


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    title: str
    section: str
    text: str


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _split_large_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = _normalize_whitespace(text)
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    overlap = max(0, min(chunk_overlap, chunk_size // 2))
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            breakpoint = normalized.rfind(" ", start, end)
            if breakpoint > start + 100:
                end = breakpoint
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_markdown(text: str, *, default_title: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [
            Chunk(title=default_title, section=default_title, text=piece)
            for piece in _split_large_text(text, chunk_size, chunk_overlap)
        ]

    sections: list[Chunk] = []
    for index, match in enumerate(matches):
        heading = _normalize_whitespace(match.group(2)) or default_title
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        combined = f"{heading}\n\n{body}" if body else heading
        pieces = _split_large_text(combined, chunk_size, chunk_overlap)
        for piece in pieces:
            sections.append(Chunk(title=default_title, section=heading, text=piece))

    return sections


def chunk_adr_markdown(text: str, *, default_title: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    normalized = _normalize_whitespace(text)
    if not normalized:
        return []

    if len(normalized) <= chunk_size * 2:
        return [Chunk(title=default_title, section=default_title, text=normalized)]

    return chunk_markdown(
        text,
        default_title=default_title,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
