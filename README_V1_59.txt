PROYECTO ARANZA v1.59

Novedad: diagnóstico de base SQLite sin cambios de datos.

Uso:
  python backup_db.py inspect
  python backup_db.py inspect --source ./respaldos/aranza_YYYYMMDD.sqlite3
  python backup_db.py backup
  python backup_db.py restore --source ./respaldos/aranza_....sqlite3 --confirm

La restauración requiere detener primero el servicio. El comando inspect comprueba integridad, pero no verifica por sí solo la persistencia remota de Render.

Antes de publicar: configura ARANZA_PASSWORD, ARANZA_SESSION_SECRET, ARANZA_ALLOWED_ORIGINS, ARANZA_DB_PATH y la clave del proveedor desde las variables de entorno del servicio. Nunca subas secretos ni bases con datos personales a GitHub.
