# Proyecto Aranza v1.45

## Previsualización explicable del contexto de memoria

- Añade `GET /memory/context-preview?query=...&limit=8` para inspeccionar qué recuerdos seleccionaría el selector existente para una consulta.
- Devuelve categoría, estado, términos léxicos coincidentes, puntuación aproximada y una razón sencilla de selección.
- La consulta está limitada a la cuenta autenticada; el límite solicitado se restringe a 1–20 y el texto a 4.000 caracteres.
- No llama al proveedor de IA, no guarda la consulta en el historial y no modifica recuerdos.
- La puntuación es léxica y explicativa, no una medida semántica ni una garantía de relevancia.

## Validación

Se añadieron pruebas para coincidencias explicables, aislamiento por cuenta, validación de entrada, límite de resultados y ausencia de efectos secundarios.
