PROYECTO ARANZA v1.46

Novedad: auditoría del contexto de memoria.

Endpoint autenticado:
GET /memory/context-audit?query=...&limit=8

Permite inspeccionar cobertura léxica y posibles redundancias entre recuerdos seleccionados. Es una heurística explicativa: no mide comprensión semántica, no confirma que un recuerdo sea verdadero y puede pasar por alto sinónimos.

Privacidad y efectos secundarios:
- Solo consulta recuerdos de la cuenta autenticada.
- No llama a un proveedor de IA.
- No guarda la consulta en el historial.
- No modifica recuerdos automáticamente.
- Límite de consulta: 4.000 caracteres; límite de resultados: 1–20.

Validación local en esta entrega: `python -m py_compile main.py` y `python -m pytest -q`.
No implica despliegue ni prueba con proveedores externos.
