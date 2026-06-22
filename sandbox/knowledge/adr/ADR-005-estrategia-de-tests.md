# ADR-005 — Estrategia de tests

- **Estado:** Aceptado
- **Contexto:** Definir el mínimo de pruebas para no acumular deuda.

## Decisión

- Stack: **Vitest** + **Testing Library**.
- **Todo componente nuevo** se entrega con al menos un test de render que verifique el contenido
  visible y, si aplica, una interacción clave (regla R8).
- Se testea comportamiento observable por el usuario, no detalles de implementación.
- Los servicios (`services/`) se testean con `fetch` *mockeado*.

## Consecuencias

- Un PR que agrega un componente **sin** su `*.test.tsx` no cumple la guía.
- Antipatrón a vigilar: componentes nuevos sin archivo de test asociado.
