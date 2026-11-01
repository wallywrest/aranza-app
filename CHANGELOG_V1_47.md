# Proyecto Aranza v1.47

## Evaluación supervisada de recuperación de memoria

- Se añade `POST /memory/context-evaluate` para comparar los recuerdos recuperados por el selector actual con IDs relevantes etiquetados manualmente.
- Reporta precisión, recall, F1, IDs esperados omitidos e IDs recuperados fuera del conjunto esperado.
- Requiere entre 1 y 50 IDs esperados sin duplicados, todos pertenecientes a la cuenta autenticada.
- Limita la selección evaluada a 1–20 recuerdos.
- La evaluación no llama a un proveedor de IA, no guarda la consulta, no modifica recuerdos y no convierte las etiquetas humanas en verdad universal.
- Se añaden pruebas de métricas básicas, aislamiento entre cuentas y rechazo de IDs duplicados.

## Límites

Las métricas dependen de etiquetas humanas y de la calidad del conjunto de evaluación. Precisión, recall y F1 evalúan recuperación de IDs, no comprensión semántica ni veracidad de los recuerdos.
