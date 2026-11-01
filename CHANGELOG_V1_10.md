# Aranza v1.10

## Ajustes de cuenta y endurecimiento web

- Añade cambio de nombre de usuario desde el menú lateral.
- Revalida la contraseña actual antes de cambiar el usuario.
- Normaliza el nombre a minúsculas y valida longitud de 3 a 32 caracteres con un conjunto seguro de caracteres.
- Revoca todas las sesiones de la cuenta al cambiar el usuario; exige iniciar sesión de nuevo.
- Añade encabezados de seguridad: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`.
- Añade `Cache-Control: no-store` a rutas sensibles, incluidas autenticación, cambio de credenciales y exportación.
- Añade HSTS cuando la petición llega por HTTPS.

## Validación

- `python -m py_compile main.py`
- `python -m pytest -q`
- No se ha desplegado a producción. Haz respaldo de SQLite y prueba primero con una copia de la base de datos real.

## Límites

- Sigue siendo una única cuenta inicial; no hay registro multiusuario.
- No hay recuperación por correo. No se debe implementar una recuperación improvisada sin un canal de verificación seguro.
