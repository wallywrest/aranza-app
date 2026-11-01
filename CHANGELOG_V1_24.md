# Aranza v1.24

## Memoria contextual más robusta
- La selección de recuerdos toma en cuenta el mensaje actual y hasta dos mensajes recientes del usuario en la conversación activa.
- El mensaje actual se pondera duplicándolo en la consulta léxica, para reducir el riesgo de que el historial anterior desplace la petición actual.
- La búsqueda local normaliza acentos y contempla algunas terminaciones comunes del español.
- No requiere servicios externos, embeddings, claves API ni nuevos paquetes.

## Límites
- La recuperación sigue siendo léxica y heurística, no una búsqueda semántica real.
- Solo se considera el historial de la conversación activa que ya está disponible para Aranza.
