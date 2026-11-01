# Proyecto Aranza v1.55

- Mejora conservadora de selección contextual: cuando existe una coincidencia léxica fuerte, filtra recuerdos cuya puntuación es igual o inferior a la mitad de la mejor coincidencia.
- Mantiene coincidencias débiles si no existe un candidato fuerte, para no perder contexto en consultas cortas o ambiguas.
- Añade pruebas contra distractores que solo comparten una parte genérica del tema.
- Sin llamadas a proveedores externos, cambios automáticos de memoria ni migraciones de base de datos.
