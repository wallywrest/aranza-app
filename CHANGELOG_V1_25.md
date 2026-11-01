# Aranza v1.25

## Vista previa del contexto de memoria
- Nuevo endpoint autenticado `POST /memory/preview`.
- Permite enviar una consulta y ver qué recuerdos seleccionaría Aranza, con categoría e identificador.
- Límite configurable entre 1 y 20 recuerdos; la consulta admite hasta 8,000 caracteres.
- La respuesta indica cuántos recuerdos existen, cuántos se seleccionaron y aclara que la selección es léxica.
- La vista previa no crea, edita ni elimina recuerdos.
- La consulta queda limitada a los recuerdos de la cuenta autenticada.

## Validación
- `python -m py_compile main.py`
- `python -m pytest -q`: 74 pruebas aprobadas.

## Límites
- Es un endpoint de API, todavía no una pantalla visual en la interfaz.
- No se ha desplegado ni probado con proveedores reales de modelos.
