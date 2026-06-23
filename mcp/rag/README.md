# MCP RAG

Local knowledge retrieval for the React reviewer.

## What it does

- indexes `sandbox/knowledge/**/*.md`
- chunks conventions, a11y checklists, and component catalog documents by Markdown sections
- treats each ADR file as a single preferred chunk when it stays reasonably short
- stores a local TF-IDF retrieval index on the runner
- exposes retrieval through MCP so the reviewer can query guidance during a PR review

## Files

- `index_knowledge.py`: builds or refreshes the local index
- `server.py`: MCP server exposing retrieval tools
- `chunking.py`: Markdown chunking helpers
- `retrieval.py`: index loading and search logic
- `config.json`: chunking and retrieval defaults

## Local setup

```bash
uv venv .venv
uv pip install -r mcp/rag/requirements.txt
python mcp/rag/index_knowledge.py
python mcp/rag/server.py
```

## Runtime model

- `Node.js` is used by the workflow for the sandbox app, Playwright installation, and `opencode-ai` execution.
- `Python` is used by the RAG indexer and the MCP knowledge server.

## Runner storage

For the workflow, the recommended index location is outside the git worktree so it survives future runs on a self-hosted runner.

Example:

```bash
export RAG_INDEX_DIR="$HOME/.cache/ai-code-reviewer-config/rag-index"
python mcp/rag/index_knowledge.py --index-dir "$RAG_INDEX_DIR"
python mcp/rag/server.py
```

## Knowledge authoring assumptions

- `sandbox/knowledge/conventions/`, `sandbox/knowledge/a11y/`, and `sandbox/knowledge/components/` should prefer one guideline per `##` section so each section remains a clean retrieval unit.
- `sandbox/knowledge/adr/` should prefer short, single-decision ADR files so one file can usually remain one coherent retrieval unit.
- If an ADR grows too large, the indexer falls back to section-based chunking to avoid oversized retrieval payloads.

## MCP tools

- `search_knowledge(query, category?, top_k?)`
- `read_knowledge_document(source_path)`

## Notes

- The reviewer still keeps `R1`-`R8` embedded in its prompt.
- The MCP knowledge base complements those rules with ADRs, extended rationale, a11y details, and component catalog guidance.
- The workflow stores the persistent index outside the git worktree on the self-hosted runner and rebuilds it only when `sandbox/knowledge/` or the RAG config changes.
