ARANZA V1.6 - PARCHE DE DESARROLLO

Cambio principal:
El límite de intentos de inicio de sesión ahora comprueba y registra fallos dentro de una transacción de escritura SQLite. Esto reduce el riesgo de que peticiones concurrentes se salten el límite por una condición de carrera.

Archivos principales:
- main.py: backend actualizado
- index.html: cliente web
- backup_db.py: respaldo y restauración SQLite
- test_*.py: pruebas automatizadas
- CHANGELOG_V1_6.md: detalle de cambios y límites

Pruebas locales: ejecutar `python -m pytest -q`.

No desplegar directamente sin revisar las variables de entorno, el almacenamiento persistente, CORS, HTTPS, copias de seguridad y la configuración del proveedor. El proyecto sigue siendo de un solo perfil con contraseña compartida; todavía no tiene cuentas multiusuario aisladas.
