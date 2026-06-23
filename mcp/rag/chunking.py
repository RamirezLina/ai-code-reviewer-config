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


def _split_with_context_prefix(
    body: str,
    *,
    prefix: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    normalized_prefix = _normalize_whitespace(prefix)
    normalized_body = _normalize_whitespace(body)

    if not normalized_body:
        return [normalized_prefix] if normalized_prefix else []

    if not normalized_prefix:
        return _split_large_text(normalized_body, chunk_size, chunk_overlap)

    available_size = max(200, chunk_size - len(normalized_prefix) - 1)
    body_pieces = _split_large_text(normalized_body, available_size, chunk_overlap)
    return [f"{normalized_prefix} {piece}" for piece in body_pieces]


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

    adr_prefix = f"ADR: {default_title}"
    if len(normalized) <= int(chunk_size * 1.5):
        return [Chunk(title=default_title, section=default_title, text=f"{adr_prefix} {normalized}")]

    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [
            Chunk(title=default_title, section=default_title, text=piece)
            for piece in _split_with_context_prefix(
                text,
                prefix=adr_prefix,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        ]

    sections: list[Chunk] = []
    for index, match in enumerate(matches):
        heading = _normalize_whitespace(match.group(2)) or default_title
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip() or heading
        prefix = f"ADR: {default_title} Section: {heading}"
        pieces = _split_with_context_prefix(
            body,
            prefix=prefix,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        for piece in pieces:
            sections.append(Chunk(title=default_title, section=heading, text=piece))

    return sections
