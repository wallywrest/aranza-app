# Aranza v1.16

## Búsqueda web controlada
- Nuevo módulo `busqueda_web.py` para consultar un endpoint fijo de búsqueda web.
- Nuevo endpoint autenticado `POST /tools/web-search`.
- Valida consultas y limita longitud y cantidad de resultados.
- Solo devuelve enlaces HTTP/HTTPS válidos y evita aceptar destinos arbitrarios como entrada, para no convertirse en un proxy abierto.
- Los errores externos no exponen detalles internos ni credenciales.
- La respuesta advierte que los fragmentos son pistas y que las fuentes deben contrastarse.

## Límites conocidos
- La herramienta devuelve resultados y fragmentos; no abre ni verifica automáticamente las páginas de destino.
- Requiere conectividad saliente del servidor con el servicio de búsqueda.
- No se ha integrado todavía un botón de búsqueda web en la interfaz.
- No se han hecho llamadas reales al servicio durante las pruebas; se usa transporte HTTP simulado.
- No desplegado en producción.
