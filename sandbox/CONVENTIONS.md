# Guía de convenciones — Frontend React

Estas son las reglas que tu agente `react-reviewer` debe hacer cumplir al revisar un PR. Cada regla
tiene un identificador (`R1`…`R8`) para que el agente pueda referenciarla en sus comentarios.

| ID | Regla |
|----|-------|
| **R1** | **Un componente por archivo**, nombrado en `PascalCase`, en archivos `.tsx`. |
| **R2** | **TypeScript estricto**: prohibido `any`. Las props se tipan con `interface` o `type`. |
| **R3** | **Rules of Hooks**: los hooks (`useState`, `useEffect`, …) solo se llaman en el nivel superior del componente. Nunca dentro de condicionales, loops o funciones anidadas. |
| **R4** | **Sin estilos inline** (`style={{ … }}`). Usar **CSS Modules** (`*.module.css`) o tokens del design system. |
| **R5** | **Las llamadas de red** (`fetch`, `axios`, …) viven en la capa `src/services/`. **Nunca** directamente dentro de un componente. |
| **R6** | **Accesibilidad**: toda `<img>` lleva `alt`; todo botón **solo-ícono** lleva `aria-label`. |
| **R7** | **Sin `console.log`** (ni `console.debug`) en el código de la app. |
| **R8** | **Todo componente nuevo** se entrega con su test (`*.test.tsx`). |

> El revisor debe ser **preciso**: comentar solo incumplimientos reales y citar la regla (`R#`).
> Un código que *parece* sospechoso pero **cumple** la guía no debe marcarse como error.
