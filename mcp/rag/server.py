from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from retrieval import KnowledgeIndexError, get_document, search_index


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX_DIR = REPO_ROOT / "mcp" / "index"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")

mcp = FastMCP("knowledge")


def _index_dir() -> str:
    return os.environ.get("RAG_INDEX_DIR", str(DEFAULT_INDEX_DIR))


def _default_top_k() -> int:
    try:
        config = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
        return int(config.get("default_top_k", 5))
    except Exception:
        return 5


def _max_excerpt_chars() -> int:
    try:
        config = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
        return int(config.get("max_excerpt_chars", 700))
    except Exception:
        return 700


def _trim_excerpt(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    limit = max(100, _max_excerpt_chars())
    trimmed: list[dict[str, Any]] = []
    for item in results:
        excerpt = item.get("excerpt", "")
        next_item = dict(item)
        if len(excerpt) > limit:
            next_item["excerpt"] = excerpt[: limit - 3].rstrip() + "..."
        trimmed.append(next_item)
    return trimmed


def _log_tool_use(tool_name: str, detail: str) -> None:
    print(f"[knowledge-mcp] {tool_name}: {detail}", file=sys.stderr, flush=True)


@mcp.tool()
def search_knowledge(query: str, category: str | None = None, top_k: int | None = None) -> dict[str, Any]:
    """Search the local sandbox knowledge base and return the most relevant excerpts."""

    _log_tool_use(
        "search_knowledge",
        f"query={query!r} category={category!r} top_k={top_k or _default_top_k()}",
    )

    try:
        results = search_index(_index_dir(), query, category=category, top_k=top_k or _default_top_k())
    except KnowledgeIndexError as exc:
        _log_tool_use("search_knowledge_error", str(exc))
        return {"error": str(exc), "results": []}

    _log_tool_use("search_knowledge_results", f"count={len(results)}")

    return {
        "query": query,
        "category": category,
        "results": _trim_excerpt(results),
    }


@mcp.tool()
def read_knowledge_document(source_path: str) -> dict[str, Any]:
    """Return all indexed chunks for a knowledge document by its source path."""

    _log_tool_use("read_knowledge_document", f"source_path={source_path!r}")

    try:
        results = get_document(_index_dir(), source_path)
    except KnowledgeIndexError as exc:
        _log_tool_use("read_knowledge_document_error", str(exc))
        return {"error": str(exc), "results": []}

    _log_tool_use("read_knowledge_document_results", f"count={len(results)}")

    return {
        "source_path": source_path,
        "results": _trim_excerpt(results),
    }


if __name__ == "__main__":
    mcp.run()
