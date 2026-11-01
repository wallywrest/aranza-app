# Aranza v1.93 — matriz de evidencia y señales temporales

- Añade identificadores estables por fuente (`S1`, `S2`, ...) dentro de cada evaluación.
- Expone una matriz compacta para comparar nivel de evidencia, contexto disponible y señal temporal.
- Detecta fechas ISO y fechas escritas en español dentro del texto de páginas efectivamente leídas.
- Calcula una señal de antigüedad configurable mediante `as_of` para pruebas reproducibles.
- Distingue fecha no identificada, hasta 90 días, 90–365 días y más de un año.
- No extrae fechas de snippets no verificados y etiqueta las fechas detectadas como candidatas.
- Mantiene la comparación conservadora de discrepancias de v1.92.

## Límites

La fecha puede ser una fecha mencionada en el cuerpo y no la fecha de publicación. No se verifica metadato editorial ni autoridad de la fuente. No se calcula una puntuación de verdad ni un ranking automático de credibilidad.
