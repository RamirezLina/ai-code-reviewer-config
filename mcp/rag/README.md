# MCP RAG

Recuperacion local de conocimiento para el agente revisor de PR del sandbox React.

## Objetivo

Este modulo permite que el agente consulte `sandbox/knowledge/**/*.md` por demanda, sin cargar toda la base de conocimiento en el prompt de cada revision.

La solucion:

- indexa los documentos Markdown de `sandbox/knowledge/`
- separa `conventions`, `a11y` y `components` por secciones Markdown
- trata los ADR de forma especial para conservar mejor su contexto
- construye un indice local TF-IDF persistente en el runner
- expone la recuperacion por MCP para que el agente consulte solo la guia necesaria durante la revision

## Archivos principales

- `index_knowledge.py`: construye o actualiza el indice local
- `server.py`: expone el MCP `knowledge` y sus tools
- `chunking.py`: aplica las reglas de particion de documentos Markdown
- `retrieval.py`: carga el indice y resuelve las busquedas
- `config.json`: define parametros de chunking y recuperacion

## Como se prepara localmente

```bash
uv venv .venv
uv pip install -r mcp/rag/requirements.txt
python mcp/rag/index_knowledge.py
python mcp/rag/server.py
```

## Modelo de ejecucion

- `Node.js` se usa en el workflow para la app del sandbox, la instalacion de Playwright y la ejecucion de `opencode-ai`.
- `Python` se usa para el indexador del RAG, la logica de retrieval y el servidor MCP del conocimiento.

## Persistencia en el runner

En la ejecucion del workflow se recomienda guardar el indice fuera del directorio Git para que sobreviva entre corridas del self-hosted runner.

Ejemplo:

```bash
export RAG_INDEX_DIR="$HOME/.cache/ai-code-reviewer-config/rag-index"
python mcp/rag/index_knowledge.py --index-dir "$RAG_INDEX_DIR"
python mcp/rag/server.py
```

## Supuestos sobre la base de conocimiento

- `sandbox/knowledge/conventions/`, `sandbox/knowledge/a11y/` y `sandbox/knowledge/components/` deben conservar una estructura clara por secciones `##`, de modo que cada seccion sea una unidad limpia de recuperacion.
- `sandbox/knowledge/adr/` debe conservar ADR cortos y centrados en una sola decision cuando sea posible.
- Si un ADR crece demasiado, el indexador lo divide por secciones para evitar chunks excesivamente largos, pero mantiene contexto de `ADR` y `Section` en cada fragmento.

## Tools MCP

- `search_knowledge(query, category?, top_k?)`
- `read_knowledge_document(source_path)`

## Notas

- El agente mantiene embebidas las reglas `R1` a `R8` definidas en `sandbox/CONVENTIONS.md`.
- Esta base de conocimiento no reemplaza esas reglas; las complementa con ADR, justificacion extendida, detalles de accesibilidad y guia de componentes.
- El workflow reconstruye el indice solo cuando cambia `sandbox/knowledge/` o `mcp/rag/config.json`; si no hay cambios, reutiliza el indice persistido en el runner.
