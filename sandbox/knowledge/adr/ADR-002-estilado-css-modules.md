# ADR-002 — Estilado con CSS Modules

- **Estado:** Aceptado
- **Contexto:** Necesitamos estilos con *scope* local, cacheables y compatibles con el design system.

## Decisión

- Todo estilo va en un archivo `*.module.css` junto al componente.
- **Prohibido** `style={{…}}` inline (regla R4), salvo valores verdaderamente dinámicos calculados en
  runtime (p. ej. una posición en px que depende de medición), que deben justificarse en el PR.
- Los tokens de color/espaciado provienen de variables CSS del design system, no de literales.

## Consecuencias

- Estilos predecibles y reutilizables; sin colisiones de nombres.
- **Nota para revisores:** una clase de CSS Module puede llamarse `inline`, `flex`, etc. El nombre no
  la convierte en estilo inline. La violación de R4 es el **atributo `style`**, no el nombre.
