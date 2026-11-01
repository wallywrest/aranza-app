PROYECTO ARANZA v1.36

Cambio principal:
La vista previa de memoria ahora explica de forma heurística por qué cada recuerdo activo se seleccionó o quedó fuera. Muestra términos coincidentes y distingue entre falta de coincidencias, límite de resultados y posible duplicación léxica. La interfaz enseña todos los seleccionados y hasta ocho ejemplos excluidos.

Validación local prevista:
- python -m py_compile main.py
- python -m pytest -q
- node --check sobre el JavaScript extraído de index.html
- verificación de integridad del ZIP

Limitación: esto explica reglas locales de selección léxica, no el razonamiento interno del proveedor de IA. No se ha desplegado ni se ha probado extremo a extremo en navegador con proveedor real.

Haz una copia de seguridad de la base de datos antes de integrar el parche.
