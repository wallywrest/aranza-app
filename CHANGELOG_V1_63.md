# Aranza v1.63

## Recuperación segura de SQLite

- La restauración elimina los archivos laterales `-wal` y `-shm` de la base anterior antes de sustituir el archivo principal, evitando que registros residuales se asocien con la base restaurada.
- Se conserva el respaldo preventivo de la base actual antes de modificarla.
- Se añadieron pruebas para comprobar que los archivos laterales antiguos no sobreviven a una restauración correcta y que los datos anteriores quedan en la copia de seguridad.

## Operación

La restauración debe ejecutarse con el servicio detenido. La eliminación de archivos laterales no sustituye esa condición. Las pruebas locales no verifican un despliegue real ni la configuración del disco persistente del proveedor.
