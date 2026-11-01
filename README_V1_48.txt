PROYECTO ARANZA v1.48

Novedad: banco de regresión reproducible para la recuperación de memoria.

Archivo nuevo:
- test_memory_benchmark.py: casos de evaluación para coincidencia directa, acentos, consultas de proyectos, ausencia de coincidencia, recuerdos archivados y métricas cero.

Ejecutar pruebas desde esta carpeta:
  python -m pytest -q

Validación complementaria:
  python -m py_compile main.py

Las etiquetas de relevancia son ejemplos supervisados. Las métricas describen el comportamiento de recuperación en esos casos, no comprensión semántica ni veracidad general. No se ha realizado despliegue de producción ni prueba con proveedor externo.
