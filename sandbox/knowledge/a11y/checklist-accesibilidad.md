# Checklist de accesibilidad (operativo)

Derivado de [`../adr/ADR-004-accesibilidad-baseline.md`](../adr/ADR-004-accesibilidad-baseline.md).
Úsalo al revisar un PR.

## Imágenes
- [ ] Toda `<img>` tiene `alt`. Decorativa → `alt=""`. Informativa → texto descriptivo.

## Controles interactivos
- [ ] Todo `<button>`/`<a>` tiene **nombre accesible** (texto visible o `aria-label`).
- [ ] Botón **solo-ícono** → `aria-label` obligatorio. *(causa típica de hallazgo)*
- [ ] No se usa `<div onClick>` como botón; se usa `<button>`.

## Color y foco
- [ ] La información no depende **solo** del color.
- [ ] El foco es visible; el orden de tabulación es lógico.

## Formularios
- [ ] Cada input tiene `<label>` asociado (`htmlFor`/`id`).

## Señales de incumplimiento frecuentes
- Botón de ícono (cerrar, refrescar 🔄, menú ☰) sin `aria-label`.
- `<img>` sin `alt`.
- Texto de bajo contraste o estado comunicado solo por color.
