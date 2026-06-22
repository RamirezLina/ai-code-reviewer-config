# Catálogo de componentes canónicos

Referencia de componentes aprobados, sus props y cuándo usarlos. El revisor puede consultar este
catálogo para sugerir reutilización en vez de reinventar.

## `UserCard`
- **Props:** `{ user: User }`.
- **Uso:** mostrar la identidad de un usuario (avatar + nombre).
- **Notas:** la `<img>` del avatar siempre lleva `alt` (`Avatar de {nombre}`). Estilos en
  `UserCard.module.css`.

## `IconButton` (canónico)
- **Props esperadas:** `{ icon: ReactNode; onClick: () => void; ariaLabel: string }`.
- **Uso:** acciones representadas solo por un ícono (refrescar, cerrar, menú).
- **Regla dura:** al ser solo-ícono, **requiere `aria-label`** (R6 / ADR-004). Estilos por CSS Module,
  no inline (R4 / ADR-002).

## `StatusBadge`
- **Props:** `{ level: 'ok' | 'warn' | 'error'; pollMs?: number }`.
- **Uso:** reflejar el estado de un servicio.
- **Notas:** el color se acompaña del texto del nivel (no depende solo del color — ADR-004). Si hace
  *polling*, debe limpiar su `setInterval` en el cleanup del `useEffect`.

## Cuándo crear un componente nuevo
- Si no existe uno equivalente en el catálogo.
- Si el existente no cubre el caso con sus props actuales (preferir extender props a duplicar).
- Todo componente nuevo: PascalCase, un archivo, su CSS Module y su test (R1, R4, R8).
