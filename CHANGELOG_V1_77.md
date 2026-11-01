# Aranza v1.77

## Primera base PWA instalable

- Se añade `manifest.webmanifest` con nombre, icono, colores y modo standalone.
- Se añade icono SVG propio de Aranza.
- Se registra el Service Worker en navegadores compatibles.
- El Service Worker almacena únicamente el shell público de la aplicación (raíz, manifiesto e icono).
- Las rutas API, solicitudes autenticadas, métodos distintos de GET y recursos externos quedan fuera de caché.
- En pérdida de conexión se puede recuperar la carcasa de la app; las funciones que requieren backend/modelo siguen necesitando internet.

## Seguridad y límites

- No se guardan respuestas privadas, tokens, sesiones, archivos ni conversaciones en Cache Storage.
- Esta versión no implementa sincronización offline ni cola de mensajes.
- La instalación depende del navegador y de HTTPS (o localhost durante desarrollo).
