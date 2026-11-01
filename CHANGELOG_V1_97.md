# Aranza v1.97 — Búsqueda global explicable en la biblioteca

## Implementado
- Nuevo módulo `conocimiento.py` con normalización Unicode y tokenización en español.
- Búsqueda local ponderada sobre título, consulta, etiquetas, resumen y metadatos/snippets de fuentes.
- Ranking por relevancia con ponderación de campos, frecuencia inversa aproximada y cobertura de términos.
- La API devuelve términos coincidentes, cobertura, puntuación y método utilizado.
- La interfaz de biblioteca usa el endpoint de ranking al buscar y muestra por qué coincidió cada expediente.
- Límite de 500 expedientes inspeccionados y 50 resultados por petición.

## Privacidad y límites
- La búsqueda se ejecuta localmente en el backend y filtra por `account_id`.
- No envía consultas ni contenido de la biblioteca a proveedores externos.
- Es recuperación léxica ponderada, NO búsqueda semántica neuronal ni embeddings. No comprende sinónimos de forma general.
- El índice se calcula al consultar; no crea vectores ni cambia el esquema de la base de datos.

## Validación
- Pruebas de ranking, fuentes, validación de consulta, aislamiento de cuenta e interfaz.
- Sin despliegue en Render ni prueba de producción.
