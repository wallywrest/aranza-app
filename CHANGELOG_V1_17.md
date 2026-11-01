# Aranza v1.17

## Integración de búsqueda web en el chat
- Se añadió un botón 🌐 para activar/desactivar la búsqueda web desde el compositor.
- Con la búsqueda activa, el cliente consulta `/tools/web-search`, pasa títulos, URLs y fragmentos al chat como contenido externo no confiable y solicita referencias numeradas.
- La respuesta muestra al final las URLs devueltas por el buscador para que el usuario pueda inspeccionarlas.
- Se mantienen búsqueda desactivada por defecto y autenticación del endpoint.

## Límites conocidos
- Los resultados se basan en títulos y fragmentos del buscador; no se descargan ni verifican páginas completas.
- La búsqueda requiere conexión al endpoint externo configurado en `busqueda_web.py`.
- La suite automatizada valida el backend y la sintaxis, pero no prueba el navegador real ni llamadas externas en vivo.
