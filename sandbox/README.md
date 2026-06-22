# Sandbox — App React del cliente (simplificada)

App mínima en **React + TypeScript + Vite**, con tests en **Vitest**. Representa el frontend del
cliente. El código de `main` **cumple** la guía de [`CONVENTIONS.md`](./CONVENTIONS.md) y sirve de
ejemplo de referencia para tu agente.

## Requisitos

- Node.js 20+

## Puesta en marcha

```bash
npm install
npm run dev        # arranca la app
npm test           # corre los tests (vitest)
npm run build      # type-check + build
```

## Estructura

```
src/
├── main.tsx
├── App.tsx
├── services/
│   └── api.ts                  # capa de red (R5)
└── components/
    ├── UserCard.tsx            # componente de ejemplo, cumple la guía
    ├── UserCard.module.css
    └── UserCard.test.tsx

knowledge/                      # base de conocimiento → la indexa tu RAG (vía MCP)
├── conventions/frontend-guidelines.md   # R1–R8 con rationale y ejemplos
├── adr/ADR-001..005.md                  # decisiones de arquitectura
├── components/catalogo-componentes.md   # componentes canónicos y sus props
└── a11y/checklist-accesibilidad.md
```

> `CONVENTIONS.md` es el **checklist corto y autoritativo** (R1–R8). `knowledge/` es el **corpus
> extendido** (rationale, ADRs, catálogo) que tu agente debe consultar por recuperación, no cargándolo
> entero en el prompt.

El cambio que debes revisar con tu agente está en [`../pr/`](../pr). Sigue
[`../pr/INSTRUCCIONES-PR.md`](../pr/INSTRUCCIONES-PR.md).
