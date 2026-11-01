PROYECTO ARANZA v1.47

Novedad: evaluación supervisada de recuperación de memoria.

Endpoint:
POST /memory/context-evaluate

Ejemplo de cuerpo JSON:
{
  "query": "practicar inglés conversación",
  "expected_memory_ids": [12, 15],
  "limit": 8
}

Los IDs esperados deben pertenecer a la cuenta autenticada y ser seleccionados por una persona como relevantes para la consulta. La respuesta incluye precisión, recall, F1, recuerdos esperados omitidos y recuerdos recuperados que no estaban etiquetados como esperados.

Esta función no llama a modelos externos, no persiste la consulta y no modifica recuerdos. Las métricas describen la recuperación respecto a las etiquetas humanas; no demuestran comprensión semántica ni verdad.

Validación local de esta versión: 125 pruebas automatizadas superadas; compilación Python y sintaxis JavaScript superadas. El paquete no implica despliegue ni prueba con proveedores externos.
