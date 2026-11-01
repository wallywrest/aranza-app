# Aranza v1.71

## Validación de manifiestos antes de restaurar

- Se centralizó la verificación de manifiestos de respaldo y sus hashes SHA-256.
- `verify-restore` ahora valida el manifiesto cuando existe y reporta `manifest_status` y `checksum_verified`.
- `restore` rechaza manifiestos ilegibles, incompatibles o con tamaño/hash discrepante antes de crear una copia de seguridad previa o modificar el destino.
- Se mantienen compatibles los respaldos heredados sin manifiesto; la respuesta los identifica como `missing` en la prueba aislada.
- Se añadieron pruebas para hash alterado, tamaño alterado, verificación correcta, preservación de la base activa y compatibilidad heredada.

La verificación SHA-256 detecta cambios respecto del manifiesto, pero no protege contra un atacante capaz de modificar tanto el respaldo como su manifiesto. Para eso se necesitaría una firma o un manifiesto guardado en un sistema separado.
