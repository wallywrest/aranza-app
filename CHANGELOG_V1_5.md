# Aranza v1.5: exportación y consistencia de conversaciones

## Cambios
- Se añadió `GET /export`, protegido por sesión, que exporta mensajes y memorias como JSON descargable.
- La exportación incluye formato, fecha UTC y alcance explícito de perfil único.
- Corregido un error previo que intercambiaba el contenido y la categoría al guardar memorias nuevas.
- El guardado de pregunta y respuesta ahora usa una sola transacción SQLite para evitar intercambios parcialmente guardados.
- Versión declarada de la API actualizada a `1.5.0`.

## Validación local
- `python -m py_compile main.py backup_db.py`
- `python -m pytest -q`

## Nota de migración
- Los recuerdos guardados por versiones anteriores pueden tener contenido y categoría intercambiados por el error previo. Esta versión no los reescribe automáticamente para evitar alterar datos ambiguos; deben revisarse antes de una migración correctiva.

## Límites importantes
- La aplicación continúa siendo de un solo perfil compartido; esto NO implementa cuentas multiusuario ni aislamiento entre personas.
- La exportación contiene datos personales en texto legible. Debe guardarse en un lugar privado.
- No se desplegó el parche ni se verificó la configuración de hosting.
