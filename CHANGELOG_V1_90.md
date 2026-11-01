# Aranza v1.90 — investigación web acotada

## Cambios

- El planificador distingue entre una búsqueda rápida (`web_search`) y una solicitud explícita de investigación (`web_research`).
- En el chat, la investigación busca hasta tres resultados y trata de leer como máximo dos páginas públicas.
- La lectura comprueba que la URL devuelta corresponde al mismo destino solicitado antes de incorporar el texto.
- Se impone un límite global de 24 segundos a la investigación por turno.
- El contexto externo se etiqueta como no confiable y diferencia fragmentos de búsqueda de páginas leídas.
- `tool_trace` informa herramienta, estado, duración, cantidad de resultados y páginas leídas.
- Si hay error o timeout, Aranza informa la limitación y no inventa fuentes.

## Límites y privacidad

- La investigación es de solo lectura. No realiza acciones externas ni ejecuta código.
- La consulta se envía al proveedor de búsqueda web y las páginas públicas se solicitan desde el servidor.
- Máximo una herramienta lógica, tres resultados, dos lecturas de página y 24 segundos por turno.
- El texto de páginas externas puede estar incompleto o ser malicioso; se trata como datos no confiables.

## Validación

- 276 pruebas automatizadas superadas en entorno local.
- Compilación Python correcta para los módulos principales.
- No se realizó despliegue a Render ni pruebas de producción con proveedores externos.
