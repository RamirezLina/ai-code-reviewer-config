from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from chunking import chunk_adr_markdown, chunk_markdown


RULE_RE = re.compile(r"\bR[1-8]\b")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_DIR = REPO_ROOT / "sandbox" / "knowledge"
DEFAULT_INDEX_DIR = REPO_ROOT / "mcp" / "index"
CONFIG_PATH = Path(__file__).with_name("config.json")


def read_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or refresh the local knowledge index.")
    parser.add_argument("--source-dir", default=os.environ.get("RAG_SOURCE_DIR", str(DEFAULT_SOURCE_DIR)))
    parser.add_argument("--index-dir", default=os.environ.get("RAG_INDEX_DIR", str(DEFAULT_INDEX_DIR)))
    return parser.parse_args()


def compute_source_hash(paths: list[Path], config: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(config, sort_keys=True).encode("utf-8"))
    for path in paths:
        digest.update(str(path.relative_to(REPO_ROOT)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def detect_doc_type(relative_path: Path) -> str:
    parts = relative_path.parts
    if len(parts) >= 3:
        return parts[2]
    return "general"


def build_documents(source_dir: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    markdown_files = sorted(source_dir.rglob("*.md"))
    documents: list[dict[str, Any]] = []
    for path in markdown_files:
        relative_path = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        title = path.stem
        doc_type = detect_doc_type(relative_path)
        if doc_type == "adr":
            chunks = chunk_adr_markdown(
                text,
                default_title=title,
                chunk_size=int(config["chunk_size"]),
                chunk_overlap=int(config["chunk_overlap"]),
            )
        else:
            chunks = chunk_markdown(
                text,
                default_title=title,
                chunk_size=int(config["chunk_size"]),
                chunk_overlap=int(config["chunk_overlap"]),
            )
        for index, chunk in enumerate(chunks):
            rule_refs = sorted(set(RULE_RE.findall(chunk.text)))
            documents.append(
                {
                    "chunk_id": f"{relative_path.as_posix()}::{index}",
                    "source_path": relative_path.as_posix(),
                    "doc_type": doc_type,
                    "title": chunk.title,
                    "section": chunk.section,
                    "rule_refs": rule_refs,
                    "text": chunk.text,
                }
            )
    return documents


def should_rebuild(index_dir: Path, source_hash: str) -> bool:
    manifest_path = index_dir / "manifest.json"
    if not manifest_path.exists():
        return True
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    return manifest.get("source_hash") != source_hash


def save_index(index_dir: Path, documents: list[dict[str, Any]], source_hash: str) -> None:
    texts = [item["text"] for item in documents]
    vectorizer = TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)

    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "documents.json").write_text(
        json.dumps({"documents": documents}, ensure_ascii=True, indent=2), encoding="utf-8"
    )
    joblib.dump(vectorizer, index_dir / "vectorizer.joblib")
    joblib.dump(matrix, index_dir / "matrix.joblib")
    (index_dir / "manifest.json").write_text(
        json.dumps(
            {
                "built_at": datetime.now(timezone.utc).isoformat(),
                "document_count": len(documents),
                "source_hash": source_hash,
            },
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    index_dir = Path(args.index_dir).resolve()
    config = read_config()

    if not source_dir.exists():
        raise SystemExit(f"Knowledge source directory does not exist: {source_dir}")

    markdown_files = sorted(source_dir.rglob("*.md"))
    if not markdown_files:
        raise SystemExit(f"No markdown files found under: {source_dir}")

    source_hash = compute_source_hash(markdown_files, config)
    if not should_rebuild(index_dir, source_hash):
        print(f"Knowledge index already up to date at {index_dir}")
        return 0

    documents = build_documents(source_dir, config)
    if not documents:
        raise SystemExit("No knowledge chunks were generated.")

    save_index(index_dir, documents, source_hash)
    print(f"Knowledge index rebuilt at {index_dir} with {len(documents)} chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
