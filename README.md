# ai-code-reviewer-config

Solucion para revisar Pull Requests del sandbox React mediante un agente especializado, ejecutado desde GitHub Actions sobre un self-hosted runner y apoyado por un RAG local expuesto por MCP.

## Objetivo

La solucion implementa una revision de PR guiada por el agente indicado por el usuario en el workflow. Esta primera version expone un unico agente habilitado, `react-reviewer`, que:

- se dispara manualmente desde `workflow_dispatch`
- recibe el PR a evaluar, el agente y un prompt adicional
- revisa unicamente cambios dentro de `sandbox/`
- consulta conocimiento extendido por MCP en lugar de cargar todo `sandbox/knowledge/` en el prompt
- publica el resultado como comentario en el PR indicado

## Arquitectura resumida

- `review.yml` es un agentic workflow disparado manualmente desde GitHub Actions sobre un `self-hosted` Linux runner
- `opencode-ai` ejecuta el agente seleccionado por el usuario dentro de las opciones habilitadas; hoy solo existe `.opencode/agents/react-reviewer.md`
- el agente usa dos MCP locales definidos en `opencode.json`:
  - `knowledge`: RAG local sobre `sandbox/knowledge/`
  - `playwright`: validacion visual o de comportamiento cuando hace falta o cuando el cliente lo pida
- el indice del RAG vive fuera del repositorio, en el runner, para reutilizarse entre ejecuciones

## Estructura principal

- `.github/workflows/review.yml`: workflow manual que ejecuta la revision y comenta el PR
- `.github/agents/react-reviewer.agent.md`: mapeo del agente al formato esperado por GitHub Copilot Enterprise
- `.opencode/agents/react-reviewer.md`: agente nativo usado por el workflow actual con OpenCode
- `mcp/rag/`: indexador, retrieval y servidor MCP del conocimiento local
- `sandbox/`: aplicacion React del reto

## Como correr la solucion

### 1. Crear el PR del sandbox

1. aplica los cambios indicados en `pr/INSTRUCCIONES-PR.md`
2. crea una rama con esos cambios
3. abre un Pull Request contra la rama base del repositorio
4. toma nota del numero del PR, porque sera una entrada del workflow

### 2. Configurar GitHub Actions

La solucion esta pensada para ejecutarse desde la pestana `Actions` del repositorio.

Requisitos previos:

- un self-hosted runner Linux registrado para este repositorio. Antes de instalarlo localmente, se debe entrar a `Settings > Actions > Runners > New self-hosted runner` en GitHub, seleccionar `Linux`, y seguir las indicaciones y comandos que GitHub presenta para ese repositorio. En esta implementacion se configuro localmente sobre Ubuntu en WSL siguiendo estos pasos:
  1. instalar utilidades base como `curl`, `tar`, `git` y `unzip`
  2. crear una carpeta del runner dentro del filesystem Linux de WSL, por ejemplo `~/actions-runner`, evitando rutas montadas como `/mnt/c/...`
  3. descargar y extraer el paquete del runner desde `Settings > Actions > Runners > New self-hosted runner`
  4. ejecutar `./config.sh --url <repo-url> --token <token>` y aceptar el `runner group` por defecto
  5. iniciar el runner con `./run.sh`
  6. verificar en GitHub que el runner aparezca como `Online` o `Idle`
  7. mantener el runner iniciado para que GitHub Actions pueda asignarle el job; si `./run.sh` no esta activo, el workflow quedara esperando un runner disponible
- `OPENCODE_API_KEY` configurado en `Settings > Secrets and variables > Actions`
- acceso del runner a internet para instalar dependencias de Node, Python y Playwright

El workflow ya viene definido en `.github/workflows/review.yml` y expone estas entradas:

- `pr_number`: numero del Pull Request a revisar
- `agent`: agente a usar; actualmente `react-reviewer`
- `prompt`: instruccion adicional para complementar la revision

### 3. Ejecutar el workflow manualmente

1. entra a `Actions`
2. selecciona `pr-review`
3. pulsa `Run workflow`
4. diligencia:
   - `pr_number`: PR objetivo
   - `agent`: `react-reviewer`
   - `prompt`: lineamiento adicional deseado
5. ejecuta el workflow

### 4. Que hace el workflow

Durante la ejecucion el pipeline:

- consulta el PR en GitHub para obtener `base_sha`, `head_sha` y titulo
- hace checkout del commit del PR
- instala Node.js, Python 3.11 y `uv`
- crea `.venv` e instala dependencias del RAG desde `mcp/rag/requirements.txt`
- instala dependencias del sandbox e instala Chromium para Playwright MCP
- define rutas persistentes del RAG en el runner:
  - `RAG_SOURCE_DIR=${GITHUB_WORKSPACE}/sandbox/knowledge`
  - `RAG_INDEX_DIR=${HOME}/.cache/ai-code-reviewer-config/rag-index`
- construye o reutiliza el indice local del conocimiento
- genera `pr-diff.patch` y `pr-diff-stat.txt`
- ejecuta `opencode-ai run` con el agente solicitado
- publica el comentario final en el PR indicado

## RAG local por MCP

El RAG indexa `sandbox/knowledge/**/*.md` y expone dos tools MCP:

- `search_knowledge(query, category?, top_k?)`
- `read_knowledge_document(source_path)`

Decisiones principales:

- no se carga toda la base de conocimiento en el prompt del agente
- el conocimiento se recupera bajo demanda por MCP
- el indice se reconstruye solo si cambia `sandbox/knowledge/` o `mcp/rag/config.json`
- el almacenamiento persiste en el self-hosted runner para evitar rehacer chunking y vectorizacion en cada corrida

## Supuestos

- el cliente pide un `workflow_dispatch`, por lo que la revision se dispara manualmente desde GitHub Actions y no automaticamente al abrir un PR
- el objetivo del self-hosted runner no es dar “memoria” al agente como tal, sino persistir el indice del RAG y evitar reconstruirlo en cada ejecucion
- `sandbox/knowledge/` se mantiene organizado por carpetas (`adr`, `a11y`, `components`, `conventions`) y esa estructura se usa para clasificar documentos
- el agente mantiene embebidas las reglas `R1` a `R8` definidas en `sandbox/CONVENTIONS.md`, mientras que el RAG las complementa con contexto extendido
- el workflow operativo usa OpenCode porque es la herramienta disponible para ejecutar el agente de punta a punta; `.github/agents/` se mantiene para mapear la solucion al modelo de agentes de Copilot Enterprise

## Mapeo a Copilot Enterprise

- `.github/agents/react-reviewer.agent.md` representa el perfil del agente esperado por GitHub Copilot Enterprise
- `mcp-servers` documenta como conectar el conocimiento por MCP
- el workflow y el self-hosted runner dejan listo el patron operativo equivalente para una adopcion posterior en Copilot Enterprise

## Video

Pendiente. Agregar aqui el enlace al video con una corrida real del pipeline.

## Documentos complementarios

- `ADR.md`: diagnostico, decisiones de arquitectura y plan de optimizacion
- `mcp/rag/README.md`: detalle tecnico del RAG local y del MCP de conocimiento
- `lineamientos/`: material base del reto
