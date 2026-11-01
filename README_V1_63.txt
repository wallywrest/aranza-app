Proyecto Aranza v1.63

Esta versión refuerza la restauración de bases SQLite. Durante una restauración confirmada, Aranza crea primero una copia de seguridad de la base existente, valida la base de origen y prepara una copia temporal validada. Antes de reemplazar el archivo principal elimina los archivos laterales -wal y -shm de la base anterior para evitar que registros residuales se mezclen con la base restaurada.

IMPORTANTE: detener el servicio antes de restaurar. No ejecutar la restauración mientras haya procesos conectados a la base. Mantener copias de seguridad fuera del mismo disco de producción para protegerse frente a pérdida del volumen.

Validación local: 196 pruebas aprobadas. Esto no equivale a una prueba de despliegue en Render.
Consulte CHANGELOG_V1_63.md para los detalles.
