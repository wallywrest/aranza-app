# Aranza v1.95 — Biblioteca visual y exportación

## Implementado
- Panel visual de biblioteca integrado en la interfaz principal.
- Búsqueda autenticada de expedientes por título, consulta y resumen (`GET /research/library?q=...`).
- Vista de detalle con consulta, resumen, fuentes, estado de lectura y evidencia.
- Exportación autenticada de cada expediente a Markdown (`GET /research/library/{id}/export`).
- Eliminación explícita de expedientes desde la interfaz.
- Se conserva el aislamiento por cuenta en listado, detalle, exportación y eliminación.

## Límites
- La biblioteca muestra los expedientes guardados explícitamente; no guarda automáticamente cada búsqueda.
- La exportación es Markdown, no PDF ni DOCX.
- No se modifica el flujo principal de chat ni se despliega a Render.
