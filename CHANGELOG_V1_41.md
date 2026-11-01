# Proyecto Aranza v1.41

## Mejora de contexto histórico de revisiones

- La búsqueda de revisiones previas ahora compara la propuesta actual con el historial de decisiones del mismo recuerdo.
- Se selecciona la revisión léxicamente más cercana que supere el umbral de 0.65, en vez de considerar únicamente la decisión más reciente del recuerdo.
- Esto evita perder una revisión relevante cuando después se registró otra decisión sobre un texto diferente.
- El contexto sigue limitado a la cuenta autenticada y no modifica ni elimina recuerdos automáticamente.
- Se añadieron pruebas de regresión para revisiones antiguas pertinentes y decisiones recientes no relacionadas.

## Limitaciones

La similitud sigue siendo léxica (Jaccard sobre tokens normalizados); no es comprensión semántica. Una decisión previa es solo contexto para la persona usuaria.
