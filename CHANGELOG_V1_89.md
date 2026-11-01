# Aranza v1.89 — ejecución acotada de herramientas desde el chat

## Cambios

- El endpoint `POST /chat` ahora conecta el planificador con el ejecutor real para solicitudes que requieren búsqueda web.
- Cuando el plan detecta `web_search`, Aranza realiza automáticamente una búsqueda pública de solo lectura con un máximo de tres resultados y una sola herramienta por turno.
- Los resultados se incorporan al contexto del modelo como datos externos no confiables. El prompt indica que no deben obedecerse instrucciones encontradas en páginas o fragmentos web.
- La respuesta incluye `tool_trace` con herramienta, estado, duración y número de resultados; `execution_plan` refleja si la búsqueda se completó o falló.
- Si la búsqueda falla, Aranza no inventa fuentes y puede responder con conocimiento general indicando la limitación.
- Las acciones con efectos externos no se ejecutan. Archivos e imágenes siguen usando sus endpoints de carga dedicados.

## Límites y privacidad

- La búsqueda envía la consulta del usuario al proveedor de búsqueda web.
- No se ejecutan compras, publicaciones, reservas, borrados, despliegues, comandos ni código.
- No hay bucle autónomo de herramientas ni llamadas ilimitadas: máximo una búsqueda y tres resultados por turno.
- Los resultados web pueden ser incompletos, engañosos o contener instrucciones maliciosas; se tratan como datos, no como autoridad.

## Validación

- Pruebas automatizadas: 273 pasaron en el entorno de desarrollo.
- No se realizó despliegue a Render ni una prueba de producción con proveedores externos.
