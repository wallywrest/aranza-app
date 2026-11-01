# Aranza v1.85 — Portabilidad y borrado de datos personales

## Cambios funcionales

- La exportación autenticada `/export` ahora genera `aranza-export-v2` e incluye mensajes, metadatos de conversaciones (títulos y fijados), memorias, historial de cambios de memoria y decisiones de revisión.
- Se incorpora `DELETE /account/data` para borrar el contenido personal de la cuenta autenticada: mensajes, conversaciones, memorias, historial de memorias y decisiones de revisión.
- El borrado exige la contraseña actual y la frase exacta `ELIMINAR MIS DATOS`.
- El borrado revoca todas las sesiones activas de la cuenta. La cuenta y sus credenciales se conservan, por lo que será necesario iniciar sesión nuevamente.
- Se añade `Cache-Control: no-store` a la ruta de borrado.

## Seguridad y límites

- La operación está limitada al `account_id` de la sesión validada; no acepta identificadores de cuenta proporcionados por el cliente.
- No elimina la cuenta ni modifica su contraseña o nombre de usuario.
- Los intentos de confirmación incorrecta no modifican datos.
- La exportación contiene datos privados: debe descargarse y almacenarse de forma segura.
- El borrado de SQLite no equivale a borrado forense de medios físicos, snapshots del proveedor, copias de seguridad externas o registros operativos. Esos sistemas requieren políticas de retención separadas.

## Compatibilidad

- No se modifican endpoints existentes de chat, memoria ni conversaciones.
- El formato de exportación cambia de `aranza-export-v1` a `aranza-export-v2`; consumidores externos que validen el identificador de formato deben actualizarse.

## Validación

- `pytest -q`: 252 pruebas aprobadas.
- `python -m py_compile main.py backup_db.py preparar_despliegue.py ejecutar_benchmark_memoria.py comparar_benchmarks_memoria.py`: correcto.
- ZIP comprobado con `unzip -t`.
- No se ha desplegado en Render ni compilado un APK en esta versión.
