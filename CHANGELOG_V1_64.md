# Proyecto Aranza v1.64

## Protección de arranque ante pérdida del almacenamiento

- Se incorpora una comprobación opcional del almacenamiento persistente antes de inicializar SQLite.
- Cuando `ARANZA_REQUIRE_PERSISTENT_STORAGE=true`, el primer arranque crea la base normalmente y escribe un marcador después de inicializarla.
- En arranques posteriores, si el marcador existe pero falta la base de datos, el proceso se detiene con un error explícito en lugar de crear silenciosamente una base vacía.
- La plantilla `render.yaml` activa esta protección para el disco montado en `/var/data`.
- Se agregan pruebas para primer arranque, base ausente después de inicialización, directorio ausente y modo desactivado.

La protección es una señal de seguridad, no un sistema de respaldo. No sustituye las copias externas ni una prueba de restauración en el proveedor de alojamiento.
