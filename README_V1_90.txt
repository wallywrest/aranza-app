ARANZA v1.90
============

Novedad principal: investigación web acotada integrada en el chat.

- Solicitudes de búsqueda sencilla: hasta tres resultados públicos.
- Solicitudes explícitas de investigación: hasta tres resultados y lectura de un máximo de dos páginas.
- Límite global de ejecución de herramientas por turno: 24 segundos.
- Los textos externos se incorporan como datos no confiables, nunca como instrucciones.
- El campo tool_trace informa estado, duración, resultados y páginas leídas.
- Si la herramienta falla o excede el tiempo, Aranza no inventa fuentes.

Seguridad: no ejecuta comandos, código ni acciones externas. Archivos e imágenes
siguen utilizando sus flujos específicos. La búsqueda envía la consulta del
usuario al proveedor de búsqueda y la lectura solicita páginas públicas desde
el servidor.

Validación local: 276 pruebas automatizadas superadas y compilación Python
correcta para los módulos principales. No se ha desplegado esta versión en
Render ni se ha validado con proveedores externos en producción.

Consulta CHANGELOG_V1_90.md para el detalle técnico.
