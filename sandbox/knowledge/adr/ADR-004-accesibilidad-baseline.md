# ADR-004 — Línea base de accesibilidad

- **Estado:** Aceptado
- **Contexto:** El cliente es del sector salud; la accesibilidad (WCAG 2.1 AA) es requisito, no extra.

## Decisión

- Toda imagen lleva `alt` (descriptivo, o `alt=""` si es puramente decorativa).
- Todo control interactivo tiene un **nombre accesible**: texto visible, `aria-label` o
  `aria-labelledby`. Los botones **solo-ícono** requieren `aria-label` (regla R6).
- El foco es visible y el orden de tabulación es lógico.
- El color nunca es el único portador de información (se acompaña de texto o ícono).

## Consecuencias

- Los componentes con solo un ícono (cerrar, refrescar, menú) **fallan la revisión** si no declaran su
  propósito accesible.
- Ver checklist operativo en [`../a11y/checklist-accesibilidad.md`](../a11y/checklist-accesibilidad.md).
