ARANZA v1.16 - BÚSQUEDA WEB CONTROLADA

Incluye un nuevo endpoint autenticado:
POST /tools/web-search
JSON: {"query":"tema a investigar","limit":5}

Devuelve títulos, enlaces y fragmentos del motor de búsqueda. El límite de resultados se restringe a 1-8 y la consulta a 300 caracteres. No acepta una URL arbitraria para descargarla, reduciendo el riesgo de SSRF y de funcionar como proxy abierto.

Importante: los fragmentos no equivalen a verificación de una fuente. El endpoint aún no está conectado a un botón de la interfaz y requiere que el servidor tenga acceso a Internet. Las pruebas usan un transporte simulado, no llamadas reales al motor de búsqueda.

Instalación futura: integrar el proyecto completo cuando se cierre la etapa de desarrollo, conservar .env y la base SQLite, y hacer una copia de seguridad antes de migrar. Este ZIP es un parche de desarrollo y no ha sido desplegado.
