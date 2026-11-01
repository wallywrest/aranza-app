# Aranza v1.98

## Recuperación contextual de investigaciones previas

- Durante una conversación, Aranza busca en la biblioteca privada de la cuenta hasta 500 expedientes recientes mediante el ranking léxico local de v1.97.
- Puede incorporar hasta tres investigaciones cuando la coincidencia supera umbrales mínimos de puntuación y cobertura.
- El contexto incluye título, consulta, resumen breve, etiquetas, fecha de actualización y referencias limitadas a fuentes.
- El contexto se inyecta como material de referencia no confiable y potencialmente desactualizado. No se presenta como investigación recién verificada ni sustituye la búsqueda web actual.
- La respuesta del chat incluye `research_context` con estado, cantidad, método e identificadores recuperados para inspección.
- La búsqueda sigue siendo léxica ponderada local, no embeddings ni comprensión semántica neuronal.
- La recuperación está limitada por `account_id`; no mezcla bibliotecas entre cuentas.

## Seguridad y límites

- Solo lectura: no modifica ni elimina expedientes.
- Máximo 3 investigaciones por turno y 500 expedientes inspeccionados.
- No se ejecutan acciones externas a partir de contenido recuperado.
