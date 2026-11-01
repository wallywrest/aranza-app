Proyecto Aranza v1.28

Novedad: puedes editar un recuerdo desde el panel de memoria. La operación actualiza contenido y categoría y queda limitada a la cuenta autenticada.

Endpoint: PUT /memory/{memory_id}
JSON requerido: {"content":"texto actualizado","category":"general"}

Para esta versión se deben ejecutar las pruebas locales con:
python -m pytest -q

No se ha desplegado a producción. Mantén una copia de seguridad de la base de datos antes de probar cambios sobre datos reales.
