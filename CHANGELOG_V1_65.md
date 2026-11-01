# Proyecto Aranza v1.65

- La restauración ahora aparta temporalmente los sidecars SQLite antiguos y los devuelve si falla el reemplazo de la base.
- Se agregó `python backup_db.py doctor --source RUTA` para diagnosticar una base ausente, errores de integridad, presencia de WAL/SHM y permisos del directorio sin crear ni modificar la base.
- Se añadieron pruebas para diagnóstico no destructivo y recuperación de sidecars ante un fallo simulado de reemplazo.

La restauración sigue requiriendo detener el servicio. El diagnóstico local no sustituye la comprobación del almacenamiento en el entorno desplegado.
