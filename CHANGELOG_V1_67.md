# Aranza v1.67

## Trazabilidad de respaldos SQLite

- Cada respaldo nuevo incluye un manifiesto JSON con nombre, origen, fecha UTC, tamaño, SHA-256, integridad y cantidad de tablas.
- El manifiesto se escribe de forma atómica usando un archivo temporal y `os.replace`.
- `audit-backups` verifica el manifiesto cuando existe y detecta alteraciones de tamaño o SHA-256.
- Los respaldos heredados sin manifiesto continúan siendo válidos si pasan `PRAGMA integrity_check`; se reportan como copias sin trazabilidad.
- La auditoría informa cuántos manifiestos fueron verificados, cuántos son inválidos y cuántos respaldos son heredados.
- El comando devuelve código de error si encuentra manifiestos inválidos.

## Seguridad y límites

El manifiesto no contiene credenciales, sesiones ni contenido de tablas, pero sí registra la ruta local de origen. SHA-256 detecta cambios respecto del manifiesto, no protege frente a un atacante capaz de reemplazar ambos archivos.
