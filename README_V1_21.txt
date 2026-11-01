PROYECTO ARANZA v1.21

CAMBIOS
- La interfaz valida y normaliza las fuentes de búsqueda antes de utilizarlas.
- Descarta enlaces con protocolos no web, credenciales incrustadas, destinos locales/reservados comunes y literales IP.
- Elimina parámetros de seguimiento comunes y fuentes duplicadas.
- Antes de utilizar texto leído, comprueba que la URL devuelta corresponde al mismo origen y ruta de la fuente original. Si no coincide, descarta ese texto.
- Conserva las advertencias sobre contenido web no confiable.

INSTALACIÓN FUTURA
Este archivo es un parche de desarrollo, no una actualización desplegada. No reemplaces archivos en producción sin respaldo y pruebas con una copia de tu base de datos. Conserva tu archivo de entorno, claves y base SQLite.

VALIDACIÓN LOCAL
- Python compilado correctamente.
- JavaScript comprobado con node --check.
- 63 pruebas aprobadas con pytest.

LIMITACIONES
- Las pruebas son locales y varias verificaciones de integración son estáticas o simuladas.
- La validación del navegador es una defensa adicional, no sustituye las restricciones de red del backend.
- La lectura web aún puede fallar por DNS, bloqueos de sitios o páginas que requieren JavaScript.
