# Aranza v1.70

## Ensayo aislado de restauración de SQLite

- Añadido `verify-restore --source RUTA` para ensayar la copia de un respaldo a una base temporal.
- Verifica integridad SQLite y compara el esquema de tablas entre el respaldo y la copia restaurada.
- Informa explícitamente que la base activa y el respaldo no fueron modificados y que la copia temporal se elimina.
- Añadidas pruebas para restauración aislada exitosa y respaldo corrupto.

La función no sustituye una restauración real de ensayo en un entorno de staging y no prueba las rutas de la aplicación ni las dependencias externas.
