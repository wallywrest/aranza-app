# Aranza v1.74

## Interfaz de organización de conversaciones
- Se conectaron los controles visuales de fijar/desfijar y renombrar conversaciones con el endpoint PATCH existente.
- El listado prioriza los metadatos persistidos por el servidor frente a títulos locales antiguos.
- Se mantiene el aislamiento por cuenta y no se modifican los endpoints de chat.
- La acción de ocultar sigue siendo local al navegador; no se presenta como borrado del servidor.

## Alcance
- No incluye despliegue en Render ni pruebas de producción.
- No incluye APK, permisos nativos, voz ni carga de imágenes desde Android.
