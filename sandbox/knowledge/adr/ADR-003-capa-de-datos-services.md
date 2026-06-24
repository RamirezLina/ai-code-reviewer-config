# ADR-003 — Capa de datos en `services/`

- **Estado:** Aceptado
- **Contexto:** Las llamadas de red dispersas en componentes son imposibles de testear y cachear.

## Decisión

- Toda interacción con APIs (`fetch`, `axios`, websockets) vive en `src/services/` (regla R5).
- Cada función de servicio: tipa su entrada y salida, valida el `response.ok`, y lanza un error
  tipado en caso de fallo.
- Los componentes consumen funciones del servicio; **nunca** construyen URLs ni hacen `fetch` directo.

## Ejemplo canónico

```ts
// services/metrics.ts
export interface Metrics { total: number; series: number[] }
export async function getMetrics(): Promise<Metrics> {
  const res = await fetch('/api/metrics')
  if (!res.ok) throw new Error(`getMetrics failed: ${res.status}`)
  return (await res.json()) as Metrics
}
```

## Consecuencias

- La UI se testea con servicios *mockeados*.
- Antipatrón a vigilar: `fetch('/api/...')` dentro de un `useEffect` en un componente.
