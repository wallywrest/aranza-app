# Aranza v1.3: persistencia y recuperación de datos

## Cambios
- SQLite se configura en modo WAL y `synchronous=FULL` durante la inicialización.
- Las conexiones configuran `busy_timeout=10000` y `foreign_keys=ON`.
- Se añadió `backup_db.py` para generar respaldos usando la API de backup de SQLite, con verificación `PRAGMA integrity_check`.
- Se añadió restauración desde un respaldo verificado. Antes de modificar la base actual, se crea una copia de seguridad previa.
- La restauración exige detener el servicio y confirmar explícitamente la operación.
- Se amplió la suite con pruebas de creación de respaldo, integridad, restauración y protección frente a restaurar una base sobre sí misma.
- Versión declarada por FastAPI: 1.3.0.

## Validación local
- `python -m py_compile main.py backup_db.py`
- `python -m pytest -q`
- Resultado de esta ejecución: **7 pruebas aprobadas**.

## Límites que siguen pendientes
- No se ha probado el almacenamiento persistente del despliegue real.
- No se han configurado respaldos automáticos ni una copia externa.
- La aplicación sigue siendo de una sola contraseña compartida, no de cuentas multiusuario.
- No se ha implementado todavía el coordinador multi-modelo ni la voz.
- No se modificó el despliegue en producción.
