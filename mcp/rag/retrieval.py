from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeIndexError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def load_index(index_dir: str) -> dict[str, Any]:
    root = Path(index_dir)
    documents_path = root / "documents.json"
    matrix_path = root / "matrix.joblib"
    vectorizer_path = root / "vectorizer.joblib"
    manifest_path = root / "manifest.json"

    missing = [
        str(path.name)
        for path in (documents_path, matrix_path, vectorizer_path, manifest_path)
        if not path.exists()
    ]
    if missing:
        raise KnowledgeIndexError(
            "Knowledge index is missing required files: " + ", ".join(missing)
        )

    return {
        "documents": _read_json(documents_path)["documents"],
        "matrix": joblib.load(matrix_path),
        "vectorizer": joblib.load(vectorizer_path),
        "manifest": _read_json(manifest_path),
    }


def search_index(index_dir: str, query: str, *, category: str | None = None, top_k: int = 5) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    bundle = load_index(index_dir)
    documents = bundle["documents"]
    matrix = bundle["matrix"]
    vectorizer = bundle["vectorizer"]

    allowed_indexes = [
        idx for idx, item in enumerate(documents) if not category or item["doc_type"] == category
    ]
    if not allowed_indexes:
        return []

    query_matrix = vectorizer.transform([query])
    scores = cosine_similarity(query_matrix, matrix[allowed_indexes]).ravel()
    ranked_pairs = sorted(
        zip(allowed_indexes, scores, strict=False), key=lambda pair: pair[1], reverse=True
    )

    limit = max(1, min(top_k, 10))
    results: list[dict[str, Any]] = []
    for doc_index, score in ranked_pairs[:limit]:
        if score <= 0:
            continue
        item = documents[doc_index]
        results.append(
            {
                "score": round(float(score), 4),
                "source_path": item["source_path"],
                "doc_type": item["doc_type"],
                "title": item["title"],
                "section": item["section"],
                "rule_refs": item["rule_refs"],
                "excerpt": item["text"],
            }
        )
    return results


def get_document(index_dir: str, source_path: str) -> list[dict[str, Any]]:
    bundle = load_index(index_dir)
    return [item for item in bundle["documents"] if item["source_path"] == source_path]
