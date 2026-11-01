# Aranza v1.72

## Diseño de arquitectura Android y funcionamiento sin conexión

- Se documenta una ruta gradual PWA → Capacitor → funciones Android nativas.
- Se definen límites reales para burbujas, mosaicos de Ajustes rápidos y ventanas superpuestas en Android/HyperOS.
- Se especifican flujos previstos para imágenes, cámara, grabación y transcripción con permisos mínimos.
- Se define un alcance offline honesto: datos descargados, cola de mensajes y modelo local opcional; las herramientas remotas siguen requiriendo conexión.
- Se añaden fases y criterios de aceptación para evitar mezclar cambios móviles experimentales con el backend estable.

**Importante:** esta versión incorpora documentación y decisiones de arquitectura. No incluye todavía APK, permisos nativos, overlay, grabación, transcripción local ni modelo offline.
