Proyecto Aranza v1.58

Novedad: restauración de SQLite preparada en archivo temporal, validada antes de sustituir la base de destino. Se conservan respaldos de seguridad antes de reemplazar una base existente.

Uso:
  python backup_db.py backup --output-dir ./respaldos
  python backup_db.py restore --source ./respaldos/archivo.sqlite3 --confirm

ATENCIÓN: detener Aranza antes de restaurar. Mantener la base y los respaldos en un almacenamiento persistente y protegido. No subir bases de datos reales al repositorio Git.

Esta versión no implica que se haya desplegado o probado el servicio en Render.
