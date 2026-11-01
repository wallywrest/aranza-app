# Aranza v1.68

## Historial de auditorías de respaldos

- `audit-backups` acepta `--history-file RUTA` para registrar cada resultado como una línea JSONL.
- El historial registra fecha UTC, carpeta auditada, antigüedad máxima, conteos de copias y manifiestos, estado y error resumido.
- Registra también auditorías fallidas, incluida la ausencia del directorio, para que los fallos no desaparezcan de la bitácora.
- El archivo se abre en modo append, se vacía el búfer y se solicita `fsync`; las ejecuciones posteriores no sobrescriben el historial.
- No guarda contenido de la base, consultas, contraseñas ni sesiones. La escritura del historial solo ocurre cuando se solicita explícitamente con `--history-file`; sin esa opción, la auditoría conserva su comportamiento no destructivo.
