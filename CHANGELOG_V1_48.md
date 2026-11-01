# Proyecto Aranza v1.48

## Banco de regresión para recuperación de memoria

- Añadido `test_memory_benchmark.py` con casos reproducibles de coincidencia directa, normalización de acentos, relevancia de proyectos, consultas sin relación léxica y exclusión de recuerdos archivados.
- Los casos evalúan el endpoint supervisado `/memory/context-evaluate` con etiquetas esperadas explícitas.
- Añadida una prueba de borde para métricas cero cuando no se recupera ningún recuerdo.
- Los tests usan cuentas aisladas y comprueban que la evaluación no llame modelos, no guarde historial ni modifique automáticamente recuerdos.

## Limitaciones

Este banco mide recuperación léxica contra etiquetas de prueba, no comprensión semántica ni verdad factual. Sus resultados no deben presentarse como una medida universal de calidad; al agregar casos nuevos, las etiquetas deben revisarse manualmente.
