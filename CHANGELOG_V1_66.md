# Proyecto Aranza v1.66

## Auditoría de respaldos

- Añadido `audit_backups()` para inspeccionar respaldos SQLite sin modificarlos ni borrarlos.
- Nuevo comando `python backup_db.py audit-backups --directory ./backups --max-age-days 7`.
- El informe distingue copias válidas e inválidas, antigüedad, respaldo válido más reciente y existencia de al menos una copia válida reciente.
- La auditoría no crea el directorio si falta y no intenta reparar ni eliminar copias corruptas.
- Añadidas pruebas para respaldos válidos, corruptos, antiguos, directorios ausentes y antigüedad negativa.
