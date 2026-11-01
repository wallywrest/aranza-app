ARANZA v1.9 - CAMBIO DE CONTRASEÑA Y REVOCACIÓN DE SESIONES

NOVEDADES
- Cambia la contraseña desde el menú lateral.
- Verifica la contraseña actual y exige 12 caracteres como mínimo para la nueva.
- Revoca todas las sesiones activas de la cuenta tras el cambio. Hay que iniciar sesión de nuevo.
- La contraseña nueva permanece después de reiniciar el servidor; ARANZA_PASSWORD solo sirve para inicializar la primera cuenta.
- Las contraseñas se almacenan como hash PBKDF2-HMAC-SHA256 con salt aleatorio.

IMPORTANTE
- Sigue siendo una sola cuenta configurada, todavía no hay registro multiusuario ni recuperación por correo.
- Haz una copia de seguridad de SQLite antes de sustituir archivos en el hosting.
- Prueba primero la migración con una copia de la base de datos real.
- No está desplegada en producción. La validación se hizo localmente.

PRUEBAS
Ejecuta desde la carpeta del proyecto:
  python -m pytest -q

Resultado durante desarrollo: 22 pruebas aprobadas.
