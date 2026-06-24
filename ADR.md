# ADR - React PR Reviewer con RAG por MCP

## Diagnostico

Se requiere revisar Pull Requests del frontend React desde GitHub Actions con un agente especializado, iniciado manualmente por el usuario, con agente seleccionable y prompt adicional. La salida debe publicarse como comentario en el PR revisado.

El cliente plantea un self-hosted runner porque percibe que en runners efimeros “el agente no queda con memoria”. En la practica, lo que no persiste no es la memoria del modelo, sino los artefactos locales de retrieval. En runners efimeros habria que rehacer chunking, vectorizacion e indexacion en cada revision, aumentando tiempo, trabajo repetido y costo operativo.

Si bien GitHub Enterprise ofrece alternativas como GitHub Copilot code review, en esta solucion se selecciona un agentic workflow manual con `workflow_dispatch`, seleccion explicita del agente y control sobre el harness de ejecucion.

## Flujo de arquitectura

1. El usuario dispara `pr-review` desde GitHub Actions y define agente, prompt y PR objetivo.
2. El workflow consulta el PR objetivo, hace checkout del commit del cambio y genera los artefactos de diff.
3. En el self-hosted runner se preparan Node.js, Python y las dependencias del sandbox, Playwright MCP y RAG local.
4. El indexador valida si `sandbox/knowledge/` o `mcp/rag/config.json` cambiaron; si hubo cambios, reconstruye el indice; si no, reutiliza el indice persistido en el runner.
5. OpenCode ejecuta el agente y este aplica las reglas embebidas del sandbox.
6. Cuando necesita contexto extendido, el agente consulta el MCP `knowledge`; si requiere validar UI o comportamiento, puede usar `playwright`.
7. El workflow toma la salida final del agente y la publica como comentario en el PR indicado.

## Arquitectura y decisiones

1. Se implementa un workflow manual `workflow_dispatch` en `.github/workflows/review.yml`. Aunque el contexto del reto menciona revision automatica, el cliente tambien necesita iniciar la corrida desde GitHub Actions, elegir el agente y agregar instrucciones finales. `pr_number` se incorpora para dirigir el comentario al PR correcto.

2. La ejecucion corre en un self-hosted runner Linux. La razon principal no es “dar memoria al agente”, sino conservar el indice local del RAG entre corridas, evitar rehacer chunking y vectorizacion, reducir latencia y mantener el conocimiento on-prem.

3. Se usa OpenCode (`opencode-ai run`) como harness del workflow porque es la herramienta disponible para esta implementacion y la que actualmente tengo habilitada con API key. A la vez, se mantiene `.github/agents/react-reviewer.agent.md` y `.github/copilot-instructions.md` apuntando a `AGENTS.md`, dejando trazado el mapeo a GitHub Copilot Enterprise.

4. Se dejan dos MCP locales habilitados. `knowledge`, expuesto por `mcp/rag/server.py`, consulta la base indexada sin cargarla completa en el prompt. `playwright` queda disponible para validar comportamiento o interfaz cuando el cambio lo requiera o cuando el usuario lo pida explicitamente.

5. El RAG se implementa en Python con `scikit-learn` usando TF-IDF y similitud coseno, en lugar de embeddings y base vectorial externa. Para este reto la base de conocimiento es acotada y la prioridad es una solucion local, barata y sencilla. El enfoque evita pasar todos los lineamientos en cada revision y recupera solo la guia necesaria, reduciendo contexto y tokens.

6. El chunking respeta el formato actual de `sandbox/knowledge/`. `conventions`, `a11y` y `components` se separan por secciones Markdown; los ADR se tratan aparte. Los ADR cortos se conservan como unidad; los largos se parten por secciones y cada chunk hereda contexto de `ADR` y `Section`.

7. La reconstruccion del indice se decide mediante hash del contenido de `sandbox/knowledge/**/*.md` y de `mcp/rag/config.json`. Si no cambia, el workflow reutiliza el indice; si cambia, lo reconstruye antes de la revision.

8. Se requieren dos runtimes en el runner: Node.js para el sandbox, Playwright MCP y OpenCode; Python para el indexador, retrieval y servidor MCP del RAG. Playwright se mantiene disponible por si el agente necesita validar UI o si el usuario lo solicita.

9. La solucion corre como un agentic workflow sobre GitHub Actions con `workflow_dispatch`: el pipeline prepara contexto, habilita MCP, ejecuta el agente en el self-hosted runner y publica el resultado. No se usa GitHub Copilot code review. En cualquier alternativa basada en modelos, el costo principal sigue estando en tokens o AI credits. Si la orquestacion corriera en GitHub-hosted runners, tambien habria consumo de minutos de Actions; al usar self-hosted runner ese costo se traslada a infraestructura operada por el cliente.

10. En esta version no se define una `skill` adicional para el reviewer. El flujo de revision es estable y siempre sigue los mismos pasos base. Si en el futuro se requieren distintos formatos de comentario o criterios segun la rama destino, podria evaluarse una separacion por skills para no cargar contexto innecesario.

11. El modelo actual se selecciona dentro de las opciones disponibles de OpenCode Go con foco en costo y disponibilidad operativa. Como evolucion, se recomienda evaluar modelos con mayor rigurosidad en code review, como familias equivalentes a GPT-5 para codigo o Claude Sonnet, cuando el balance costo-calidad justifique una revision mas profunda.

12. Si la ejecucion migrara de OpenCode a GitHub Copilot, la mayor parte de la orquestacion se conservaria: `workflow_dispatch`, self-hosted runner, indice RAG persistente, arranque del sandbox, uso de MCP y publicacion del comentario. El cambio principal estaria en el harness: `opencode-ai run` seria reemplazado por la invocacion del agente definido en `.github/agents/react-reviewer.agent.md`, manteniendo `AGENTS.md` y `.github/copilot-instructions.md` como politica estable.

## Mapeo a Copilot Enterprise

- el perfil del agente vive en `.github/agents/react-reviewer.agent.md`
- el conocimiento se conecta por `mcp-servers`, configurado en `.github/agents/react-reviewer.agent.md`
- el self-hosted runner conserva el indice local y ejecuta el workflow
- OpenCode se usa como harness actual, pero la estructura del repositorio ya refleja la traduccion esperada a Copilot Enterprise; para una ejecucion completamente nativa aun habria que ajustar el workflow al mecanismo final de invocacion elegido en GitHub

## Plan de optimizacion de creditos

En plataformas como Copilot y otras ofertas de IA, además del costo por tokens generados por la respuesta final, tambien pesan los tokens de entrada y, cuando aplique, los tokens cacheados o reenviados al modelo. Por eso, incluir toda la base de lineamientos en cada prompt de revision incrementa el volumen de entrada incluso para PR pequenos.

La optimizacion principal de esta solucion es usar RAG por MCP para recuperar solo el contexto necesario. En lugar de pasar completos los ADR, guias extendidas, catalogo de componentes y checklists de accesibilidad en cada corrida, el agente consulta bajo demanda un subconjunto alineado con el diff revisado. Esto reduce tokens de entrada, evita ruido en la ventana de contexto y mantiene el foco en los lineamientos relevantes para el cambio.

Como validacion puntual, se realizo una prueba A/B sobre el mismo PR de la prueba tecnica usando el modelo `opencode-go/deepseek-v4-pro`: una corrida con RAG y otra sin RAG, inyectando todos los lineamientos desde `sandbox/knowledge/`. Los resultados observados fueron:

| Metrica | Con RAG | Sin RAG | Diferencia |
| --- | ---: | ---: | ---: |
| Input tokens | 92.676 | 125.871 | +33.195 |
| Output tokens | 6.026 | 11.273 | +5.247 |
| Total tokens | 98.702 | 137.144 | +38.442 |
| Costo aproximado | $0.0512 | $0.0775 | +$0.0263 |

Esta es una unica medicion y no debe usarse para inferir conclusiones concluyentes sobre la ventaja del uso de RAG. Sin embargo, en esta prueba concreta si se observa el comportamiento esperado: el escenario sin RAG consumio mas tokens de entrada, mas tokens totales y mayor costo, porque obligo a enviar al modelo todos los lineamientos en lugar de recuperar solo el contexto relevante.

Como criterio adicional de optimizacion, el modelo debe elegirse segun stack, complejidad del codebase y profundidad esperada del review. Un revisor React sobre una aplicacion pequena puede operar con modelos de menor costo si mantienen suficiente precision; para revisiones mas rigurosas o codebases mas complejos conviene evaluar modelos con mejor desempeno en code review, aun con mayor costo unitario.

Como estimacion cualitativa por ejecucion, los componentes de costo quedan asi:

- costo fijo bajo: instrucciones estables del agente, reglas `R1` a `R8` y prompt operativo del workflow
- costo variable medio: diff del PR y contexto adicional solicitado por el usuario
- costo variable controlado por RAG: resultados recuperados desde `knowledge` en lugar de inyectar toda `sandbox/knowledge/`
- costo opcional adicional: uso de Playwright MCP cuando se solicita validacion visual o de comportamiento

