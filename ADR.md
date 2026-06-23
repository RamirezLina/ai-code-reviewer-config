# ADR - React PR Reviewer con RAG por MCP

## Diagnostico

Se requiere revisar Pull Requests del frontend React desde GitHub Actions con un agente especializado, ejecutado desde un workflow manual donde el usuario pueda iniciar la revision, indicar el agente a utilizar y agregar instrucciones complementarias para la corrida. Adicionalmente, la salida debe publicarse como comentario en el PR revisado.

El cliente plantea el uso de un self-hosted runner porque percibe que en los runners efimeros “el agente no queda con memoria”. En la practica, lo que no persiste entre ejecuciones no es la memoria del modelo, sino los artefactos locales que soportan la recuperacion de conocimiento. Si el workflow corriera siempre en runners efimeros (como los GitHub-hosted runners), seria necesario rehacer el proceso de chunking, vectorizacion e indexacion en cada revision, aumentando tiempo de ejecucion, trabajo repetido y costo operativo.

Si bien GitHub Enterprise ofrece alternativas como GitHub Copilot code review, en esta solucion se selecciona un agentic workflow manual con `workflow_dispatch`, seleccion explicita del agente habilitado y control sobre el harness de ejecucion.

## Flujo de arquitectura

1. El usuario dispara `pr-review` desde GitHub Actions y selecciona el agente habilitado, junto con un prompt adicional y el numero de PR a revisar.
2. El workflow consulta el PR objetivo, hace checkout del commit del cambio y genera los artefactos de diff.
3. En el self-hosted runner se preparan los runtimes de Node.js y Python, junto con las dependencias del sandbox, Playwright MCP y RAG local.
4. El indexador valida si `sandbox/knowledge/` o `mcp/rag/config.json` cambiaron; si hubo cambios, reconstruye el indice; si no, reutiliza el indice persistido en el runner.
5. OpenCode ejecuta el agente seleccionado y este aplica las reglas embebidas del sandbox.
6. Cuando necesita contexto extendido, el agente consulta el MCP `knowledge`; si requiere validar UI o comportamiento, puede usar `playwright`.
7. El workflow toma la salida final del agente y la publica como comentario en el PR indicado.

## Arquitectura y decisiones

1. Se implementa un workflow manual `workflow_dispatch` en `.github/workflows/review.yml`. Aunque el contexto del reto menciona revision automatica de PR, el cliente tambien necesita poder iniciar la corrida desde GitHub Actions, elegir el agente habilitado y agregar instrucciones finales antes de ejecutar la revision. El `pr_number` se incorpora como dato operativo del workflow para dirigir el comentario al PR correcto.

2. La ejecucion corre en un self-hosted runner Linux. La razon principal no es “dar memoria al agente”, sino conservar el indice local del RAG entre corridas, evitar rehacer chunking y vectorizacion en cada revision, reducir latencia por trabajo repetido y mantener el conocimiento on-prem.

3. Se usa OpenCode (`opencode-ai run`), usando OpenCode Go como proveedor de modelos, como harness del workflow porque es la herramienta de preferencia personal disponible para esta implementacion y es la que actualmente tengo habilitada con API key. A la vez, se mantiene `.github/agents/react-reviewer.agent.md` y `.github/copilot-instructions.md` apuntando a `AGENTS.md`, ya que esa politica estable resulta mas versatil para distintos harnesses agenticos y deja trazado el mapeo a GitHub Copilot Enterprise.

4. Se dejan dos MCP locales habilitados. `knowledge`, expuesto por `mcp/rag/server.py`, sirve para consultar la base de conocimiento indexada sin cargarla completa en el prompt. `playwright` queda disponible para validar comportamiento o interfaz cuando el cambio lo requiera o cuando el usuario lo indique explicitamente en el prompt del workflow.

5. El RAG se implementa en Python con `scikit-learn` usando TF-IDF y similitud coseno, en lugar de embeddings y base vectorial externa. Para este reto la base de conocimiento es acotada y la prioridad es una solucion local, barata y sencilla. Este enfoque evita pasar todos los lineamientos en cada revision, incluso cuando el PR es pequeño, y recupera solo la guía necesaria para el cambio evaluado, reduciendo consumo de contexto y tokens.

6. El chunking respeta el formato actual de `sandbox/knowledge/` para no exigir reescritura del material fuente. `conventions`, `a11y` y `components` se separan por secciones Markdown, mientras que los ADR se tratan de forma especial. Los ADR cortos se conservan como unidad; los largos se parten por secciones, pero cada chunk hereda contexto de `ADR` y `Section` para no perder significado.

7. La reconstruccion del indice se decide mediante hash del contenido de `sandbox/knowledge/**/*.md` y de `mcp/rag/config.json`. Si el hash no cambia, el workflow reutiliza el indice persistido; si cambia, lo reconstruye antes de ejecutar la revision.

8. Se requieren dos runtimes en el runner: Node.js para el sandbox, Playwright MCP y OpenCode; Python para el indexador, retrieval y servidor MCP del RAG. Playwright se mantiene disponible por si el agente necesita validar UI o si el usuario lo solicita explicitamente.

9. La implementacion agentic workflow corre sobre un workflow de GitHub Actions con `workflow_dispatch`, el pipeline prepara contexto, habilita MCP, ejecuta el agente en el self-hosted runner y publica su resultado en el PR. No se usa GitHub Copilot code review (producto de GitHub especializado en revisiones de código). En cualquier alternativa basada en modelos, el costo principal sigue estando en el consumo de tokens o AI credits. Adicionalmente, si la orquestacion se ejecutara sobre GitHub-hosted runners, tambien habria consumo de minutos de GitHub Actions; al usar self-hosted runner ese costo no desaparece, pero se traslada a la infraestructura operada por el cliente y evita sumar minutos de runner hospedado por GitHub.

10. En esta version no se define una `skill` adicional para el reviewer. El flujo de revision es estable y siempre sigue los mismos pasos base, por lo que no era necesario agregar otra capa de instrucciones ni obligar al agente a leer archivos adicionales. Si en el futuro se requieren distintos formatos de comentario o criterios de revision segun la rama destino del PR, podria evaluarse una separacion por skills para no cargar contexto que no aplique a cada corrida.

11. El modelo actual se selecciona dentro de las opciones disponibles de OpenCode Go con foco en costo y disponibilidad operativa para esta implementacion. Como evolucion, se recomienda evaluar modelos con mayor rigurosidad en code review, como familias equivalentes a GPT-5 para codigo o Claude Sonnet, cuando el balance costo-calidad justifique una revision mas profunda.

12. Si la ejecucion migrara de OpenCode a GitHub Copilot, la mayor parte de la orquestacion actual se conservaria: `workflow_dispatch`, self-hosted runner, construccion o reutilizacion del indice RAG, arranque del sandbox, uso de MCP y publicacion del comentario en el PR. El cambio principal estaria en el harness de ejecucion: el paso `opencode-ai run` seria reemplazado por la invocacion del agente definido en `.github/agents/react-reviewer.agent.md`, manteniendo `AGENTS.md` y `.github/copilot-instructions.md` como politica estable. En una aproximacion nativa, GitHub o Copilot resolverian directamente la ejecucion del agente; en una aproximacion por CLI, el workflow seguiria invocando una herramienta de linea de comandos, pero ya orientada a Copilot en lugar de OpenCode.

## Mapeo a Copilot Enterprise

- el perfil del agente vive en `.github/agents/react-reviewer.agent.md`
- el conocimiento se conecta por `mcp-servers`, configurado en `.github/agents/react-reviewer.agent.md`
- el self-hosted runner conserva el indice local y ejecuta el workflow
- OpenCode se usa como harness actual, pero la estructura del repositorio ya refleja la traduccion esperada a Copilot Enterprise; para una ejecucion completamente nativa aun habria que ajustar el workflow al mecanismo final de invocacion elegido en GitHub

## Plan de optimizacion de creditos

En plataformas como Copilot y otras ofertas de IA, además del costo por tokens generados por la respuesta final, tambien se consideran los tokens de entrada y, cuando aplique, los tokens cacheados o reenviados al modelo. Por eso, incluir toda la base de lineamientos en cada prompt de revision incrementaría el volumen de entrada incluso para PR pequeños.

La optimizacion principal de esta solucion es usar RAG por MCP para recuperar solo el contexto necesario. En lugar de pasar completos los ADR, guias extendidas, catalogo de componentes y checklists de accesibilidad en cada corrida, el agente consulta bajo demanda un subconjunto alineado con el diff revisado. Esto reduce tokens de entrada, evita ruido en la ventana de contexto y mantiene el foco en los lineamientos realmente relevantes para el cambio.

Como criterio adicional de optimizacion, el modelo debe elegirse segun stack, complejidad del codebase y profundidad esperada del review. Un revisor React sobre una aplicacion pequeña puede operar con modelos de menor costo si mantienen suficiente precision; para revisiones mas rigurosas o codebases mas complejos conviene evaluar modelos con mejor desempeño en code review, aun con mayor costo unitario, siempre comparando costo total contra calidad de hallazgos.

Como estimacion cualitativa por ejecucion, los componentes de costo quedan asi:

- costo fijo bajo: instrucciones estables del agente, reglas `R1` a `R8` y prompt operativo del workflow
- costo variable medio: diff del PR y contexto adicional solicitado por el usuario
- costo variable controlado por RAG: resultados recuperados desde `knowledge` en lugar de inyectar toda `sandbox/knowledge/`
- costo opcional adicional: uso de Playwright MCP cuando se solicita validacion visual o de comportamiento

En una implementacion futura completamente soportada por Copilot Enterprise, este mismo criterio seguiria aplicando: reducir contexto fijo, recuperar solo lo necesario, reutilizar cache o indice local cuando sea posible y enrutar cada reviewer al modelo con mejor balance costo-calidad para su stack.
