# Guía de frontend (versión extendida)

> Esta es la versión **larga y razonada** de las convenciones. El checklist corto y autoritativo está
> en [`../../CONVENTIONS.md`](../../CONVENTIONS.md) (reglas `R1`–`R8`). Aquí se explica el *por qué* y
> se dan ejemplos. Este documento es parte del corpus que tu RAG debe poder consultar.

## R1 — Un componente por archivo, en `PascalCase`

**Por qué.** La trazabilidad importa: un archivo = un componente facilita el *code splitting*, el
*tree-shaking* y la búsqueda. Mezclar varios componentes en un archivo dificulta el *lazy loading* y
los *imports* selectivos.

- ✅ `UserCard.tsx` exporta `UserCard`.
- ❌ `widgets.tsx` exporta `UserCard`, `Avatar` y `Badge` juntos.
- Los subcomponentes triviales que solo se usan dentro del mismo componente y no se exportan son
  tolerables, pero si crecen o se reutilizan, **extráelos a su propio archivo**.

## R2 — TypeScript estricto: prohibido `any`

**Por qué.** `any` apaga el verificador de tipos justo donde más se necesita. Rompe el contrato de
datos y propaga errores silenciosos. Si no conoces el tipo, usa `unknown` y refina, o modela el tipo.

- ✅ `interface MetricsResponse { total: number; series: number[] }`
- ✅ `const [data, setData] = useState<MetricsResponse | null>(null)`
- ❌ `const [data, setData] = useState<any>(null)`
- Las props **siempre** se tipan con `interface` o `type`.

## R3 — Rules of Hooks

**Por qué.** React identifica los hooks por el **orden de llamada**. Llamarlos dentro de condicionales,
loops o funciones anidadas rompe ese orden entre renders y produce bugs difíciles de rastrear.

- ✅ Hook en el nivel superior; la condición va **dentro** del hook.
  ```tsx
  useEffect(() => { if (showChart) drawChart() }, [showChart])
  ```
- ❌ Hook dentro de la condición.
  ```tsx
  if (showChart) { useEffect(() => { /* … */ }) }
  ```

## R4 — Sin estilos inline

**Por qué.** Los estilos inline (`style={{…}}`) no se cachean, no respetan el *design system* y
dificultan el tema oscuro/claro y el responsive. Ver [`../adr/ADR-002-estilado-css-modules.md`](../adr/ADR-002-estilado-css-modules.md).

- ✅ `className={styles.card}` con un `*.module.css`.
- ❌ `style={{ padding: 8 }}`.
- ⚠️ Ojo: una clase de CSS Module **puede llamarse** `inline` sin ser un estilo inline. Lo que viola la
  regla es el atributo `style={{}}`, no el nombre de la clase.

## R5 — La red vive en `src/services/`

**Por qué.** Separar la capa de datos del render permite testear, cachear y reintentar sin tocar la UI.
Ver [`../adr/ADR-003-capa-de-datos-services.md`](../adr/ADR-003-capa-de-datos-services.md).

- ✅ El componente llama a `getMetrics()` de `services/`.
- ❌ El componente hace `fetch('/api/...')` directo dentro de un `useEffect`.

## R6 — Accesibilidad mínima

**Por qué.** Es requisito legal y de calidad para el cliente (sector salud). Ver
[`../a11y/checklist-accesibilidad.md`](../a11y/checklist-accesibilidad.md).

- ✅ Toda `<img>` con `alt` descriptivo (o `alt=""` si es decorativa).
- ✅ Todo botón **solo-ícono** con `aria-label`.
- ❌ `<button>{icon}</button>` sin etiqueta accesible.

## R7 — Sin `console.log`

**Por qué.** Ruido en producción, posible fuga de datos sensibles y degradación de performance. Usa el
logger del proyecto o elimínalo antes del merge.

## R8 — Todo componente nuevo con su test

**Por qué.** Un componente sin test es deuda inmediata. Ver
[`../adr/ADR-005-estrategia-de-tests.md`](../adr/ADR-005-estrategia-de-tests.md). El mínimo es un test
de render que verifique el contenido visible.
