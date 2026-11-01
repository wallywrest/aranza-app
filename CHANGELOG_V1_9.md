# Aranza v1.9

## Seguridad de contraseña y sesiones

- Añade `POST /change-password`, protegido por sesión y verificación de contraseña actual.
- Exige una contraseña nueva de al menos 12 caracteres.
- Al cambiar la contraseña, revoca todas las sesiones de esa cuenta y exige iniciar sesión de nuevo.
- Guarda la contraseña nueva como hash PBKDF2-HMAC-SHA256 con salt aleatorio.
- Añade `account_id` a la tabla de sesiones mediante migración aditiva, conservando las sesiones antiguas bajo `owner`.
- Corrige el arranque para que `ARANZA_PASSWORD` inicialice la primera cuenta solamente; reiniciar ya no sobrescribe una contraseña cambiada.
- El inicio de sesión usa la cuenta persistida en SQLite después del primer arranque, sin requerir que la variable `ARANZA_PASSWORD` siga presente.
- Añade acceso a “Cambiar contraseña” desde el menú lateral.

## Validación

- `python -m py_compile main.py`
- `python -m pytest -q`: 22 pruebas aprobadas durante desarrollo.
- No se ha desplegado a producción. Antes de actualizar un servidor real, hacer una copia de seguridad y probar la migración sobre una copia de la base de datos real.

## Límites que siguen pendientes

- Sigue siendo una cuenta configurada, no un sistema público de registro multiusuario.
- No hay recuperación de contraseña por correo ni panel administrativo.
- El cambio de contraseña usa cuadros de diálogo del navegador; una pantalla de configuración dedicada queda para una iteración posterior.
