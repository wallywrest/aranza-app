ARANZA v1.8 - AUTENTICACION CON CUENTA

CAMBIOS
- Acceso con nombre de usuario y contraseña.
- Hash PBKDF2-HMAC-SHA256 con salt aleatorio para el almacenamiento de contraseña.
- Sesiones emitidas con el account_id de la cuenta autenticada.
- Mensajes de error genéricos para no revelar si un usuario existe.
- Formulario de acceso actualizado.

CONFIGURACION
- ARANZA_PASSWORD: contraseña inicial/configurada en el entorno del servidor.
- ARANZA_USERNAME: nombre de usuario (por defecto: owner).
- Mantén ARANZA_SESSION_SECRET configurada con un secreto aleatorio fuerte.
- Mantén ARANZA_DB_PATH en almacenamiento persistente.

PRUEBAS
Ejecutar: python -m pytest -q
Resultado durante desarrollo: 19 pruebas aprobadas.

LIMITES
Esta versión todavía es de una sola cuenta. No tiene registro de nuevos usuarios, recuperación de contraseña ni panel de administración. No se ha desplegado en producción. Haz una copia de seguridad y valida la migración sobre una copia de la base real antes de actualizar el hosting.
