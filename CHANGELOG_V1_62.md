# Aranza v1.62

## Persistencia y recuperación
- Añade pruebas que reinicializan el esquema y verifican que conversaciones y memorias existentes sobreviven.
- Añade pruebas de lectura desde una conexión nueva, simulando peticiones posteriores o reinicio del proceso.
- Verifica que los respaldos SQLite incluyen datos confirmados que aún están en WAL.
- Verifica que la inspección de bases persistentes reporta el modo WAL y la integridad.

## Alcance
- Son pruebas locales con SQLite temporal; no sustituyen una prueba real de reinicio en Render ni validan la configuración del disco persistente del proveedor.
