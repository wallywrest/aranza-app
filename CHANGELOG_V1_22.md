# Aranza v1.22

## Investigación web integrada

- Nuevo endpoint autenticado `POST /tools/research` que realiza la búsqueda y trata de leer hasta dos páginas en un único flujo.
- Conserva hasta cinco resultados de búsqueda y su fragmento aunque la lectura de una página falle.
- Limita el texto extraído por página a 1.800 caracteres antes de devolverlo al cliente.
- Comprueba que la URL devuelta por el lector coincida en esquema, host, puerto y ruta con la fuente solicitada.
- Devuelve `pages_read` y `page_read` para distinguir páginas leídas de resultados que solo tienen fragmento.
- La interfaz ahora usa el endpoint unificado, reduciendo solicitudes cliente-servidor y centralizando la política de lectura.
- El contenido de las páginas sigue marcado como externo y no confiable antes de enviarse al modelo.

## Pruebas

- 65 pruebas automatizadas aprobadas localmente.
- Incluye autenticación del endpoint, lectura máxima de dos páginas, fallo parcial, validación de consulta y ocultación de errores internos.
- Validación de sintaxis Python y JavaScript realizada localmente.

## Limitaciones conocidas

- No se han ejecutado búsquedas reales contra DuckDuckGo ni lecturas reales de páginas en esta validación; los tests del flujo usan funciones simuladas.
- La disponibilidad depende del motor de búsqueda, la conectividad y los proveedores de modelos configurados.
- No desplegado en el servidor del usuario. Conservar una copia de seguridad antes de cualquier instalación futura.
