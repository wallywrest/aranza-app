# Aranza v1.8 - Autenticación con cuenta y hash de contraseña

## Cambios
- El inicio de sesión ahora acepta usuario y contraseña.
- Se añadió la tabla `cuentas`, con `username` único y `account_id`.
- La contraseña se transforma mediante PBKDF2-HMAC-SHA256 con salt aleatorio y 310,000 iteraciones antes de almacenarse en SQLite. No se almacena la contraseña en texto plano en la tabla de cuentas.
- El endpoint devuelve errores genéricos para usuario inexistente o contraseña incorrecta.
- El token se emite con el `account_id` asociado a la cuenta autenticada.
- La pantalla de acceso solicita usuario y contraseña, sin limitar la contraseña a seis dígitos.
- Se conserva la configuración heredada `ARANZA_PASSWORD`; `ARANZA_USERNAME` permite configurar el nombre de usuario (por defecto `owner`). Al iniciar, la cuenta configurada se crea o sincroniza con el secreto de entorno.

## Verificación
- `python -m py_compile main.py`
- `python -m pytest -q`: 19 pruebas aprobadas.

## Límites importantes
- Esta versión sigue siendo una instancia de una sola cuenta (`account_id=owner`). No añade registro público, recuperación de contraseña ni administración de múltiples usuarios.
- El secreto inicial sigue llegando desde la variable de entorno `ARANZA_PASSWORD`; la base guarda el hash, pero el proveedor de hosting debe proteger las variables de entorno.
- No se desplegó en producción. Hay que validar la migración con una copia real de la base antes de reemplazar archivos en el hosting.
