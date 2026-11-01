# Aranza v1.59

## Diagnóstico de base de datos
- Añade `python backup_db.py inspect --source RUTA` para verificar la integridad SQLite y mostrar metadatos operativos básicos sin modificar la base.
- Informa modo de journal, número de tablas de usuario, tamaño físico y tamaño lógico estimado.
- Añade pruebas de solo lectura y rechazo de bases corruptas.

## Límites
- La inspección local no demuestra que el disco de Render sea persistente ni que exista un respaldo remoto.
- La restauración debe ejecutarse con la aplicación detenida y un respaldo verificado disponible.
