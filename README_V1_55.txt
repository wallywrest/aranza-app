PROYECTO ARANZA v1.55

Cambio principal:
La recuperación de recuerdos ahora evita incluir algunos distractores léxicos débiles cuando ya existe una coincidencia claramente más fuerte. Si no existe un candidato fuerte, conserva las coincidencias parciales para no descartar contexto potencialmente útil.

Verificación recomendada antes de publicar:
  python -m py_compile main.py ejecutar_benchmark_memoria.py comparar_benchmarks_memoria.py
  python -m pytest -q
  python ejecutar_benchmark_memoria.py --output benchmark_memoria.json

El benchmark usa una base de datos temporal y no llama a modelos externos. Las métricas son heurísticas léxicas supervisadas, no una prueba de comprensión semántica.
