# Seguridad de sesiones y datos locales — v1.84

## Hallazgo confirmado en el código actual

El frontend guarda el `access_token` en `sessionStorage` (`getSessionToken`, `setSessionToken`, `clearSessionToken`). Los borradores y algunas preferencias se guardan en `localStorage`. Esto mantiene una separación razonable entre pestañas para la sesión web, pero **no equivale a Android Keystore ni a almacenamiento cifrado nativo**. No se debe afirmar que la sesión móvil ya está protegida por hardware.

## Decisión de arquitectura

Mantener el flujo web existente mientras se diseña un adaptador de sesión por plataforma:

- Web: conservar temporalmente `sessionStorage` y el logout remoto actual.
- Android: usar un plugin de almacenamiento seguro mantenido y compatible con Capacitor; evaluar Android Keystore como respaldo criptográfico, no implementar criptografía propia.
- El frontend solo debe conocer una interfaz (`get`, `set`, `clear`), no el mecanismo de almacenamiento.
- Nunca guardar claves de proveedores de IA en el cliente, preferencias, archivos de configuración empaquetados o APK.
- No almacenar contraseñas. El backend sigue siendo autoridad para expiración, revocación y permisos.

## Requisitos antes de habilitar almacenamiento nativo

1. Seleccionar y fijar versión de plugin con mantenimiento activo, licencia compatible y revisión de vulnerabilidades.
2. Verificar cifrado en reposo, comportamiento tras reinicio, bloqueo de pantalla, restauración y desinstalación.
3. Definir expiración y rotación del token en servidor; si el backend solo emite tokens de larga duración, resolverlo antes de producción móvil.
4. Limpiar credenciales al cerrar sesión y ante respuestas de autenticación inválida.
5. Evitar registrar tokens en consola, telemetría, mensajes de error o reportes Sentry.
6. Probar que el respaldo Android no exporte secretos y que una instalación restaurada no recupere una sesión revocada.
7. Revisar el manifiesto fusionado, no solo la plantilla, y probar en dispositivo físico.

## Datos locales

Los borradores actuales pueden contener texto privado. La siguiente etapa debe ofrecer controles visibles para borrar borradores, exportar conversaciones y eliminar datos locales. No se debe prometer cifrado de `localStorage`; para Android, los datos sensibles requieren almacenamiento nativo apropiado. La caché PWA debe continuar excluyendo API autenticadas, conversaciones y tokens.

## Criterios de aceptación para la implementación posterior

- La web sigue iniciando sesión y cerrando sesión sin cambios de contrato.
- Android no usa `localStorage` ni `sessionStorage` para tokens.
- Token ausente, expirado o revocado conduce al login sin bucles.
- Logout limpia almacenamiento local incluso si el servidor no responde, y comunica que la revocación remota pudo quedar pendiente.
- Ningún secreto aparece en logs, exportaciones, backups o recursos estáticos.
- Pruebas en Android físico y revisión del APK firmado antes de despliegue.

## Alcance real de v1.84

Esta versión documenta el hallazgo y fija criterios verificables. **No migra todavía el token a Keystore, no añade un plugin nativo, no genera APK y no cambia el runtime.** Se evita simular una mejora de seguridad sin poder probarla en Android.
