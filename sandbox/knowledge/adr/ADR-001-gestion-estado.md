# ADR-001 — Gestión de estado

- **Estado:** Aceptado
- **Contexto:** Necesitamos una estrategia uniforme de estado en el frontend.

## Decisión

- El **estado local** del componente se maneja con `useState`/`useReducer`.
- El **estado de servidor** (datos remotos) NO se duplica en estado global; se obtiene en la capa
  `services/` y se cachea allí. No introducimos Redux/MobX salvo necesidad demostrada.
- El estado derivado se calcula con `useMemo`, nunca se persiste como otra pieza de estado.

## Consecuencias

- Menos *boilerplate*; menos fuentes de verdad duplicadas.
- Los componentes permanecen tontos respecto al origen de los datos (se conecta con R5).
- Antipatrón a vigilar: guardar en `useState` algo que ya es derivable de props/otros estados.
