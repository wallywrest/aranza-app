PROYECTO ARANZA v1.49

Novedad: comparador de informes de benchmark para detectar regresiones entre versiones.

Archivos nuevos:
- comparar_benchmarks_memoria.py: compara precisión, recall y F1 de dos informes JSON.
- test_memory_benchmark_comparison.py: pruebas de regresiones, umbral, casos ausentes y validación de datos.
- CHANGELOG_V1_49.md: detalle de cambios y uso.

Ejemplo:
  python comparar_benchmarks_memoria.py baseline.json candidato.json --threshold 0.05 --output comparacion.json

Códigos de salida:
  0 = no se detectaron regresiones según el umbral
  1 = se detectaron regresiones
  2 = entrada inválida o error de lectura/escritura

Validación ejecutada localmente:
  python -m pytest -q
  python -m py_compile main.py comparar_benchmarks_memoria.py

Los informes comparan solo casos con el mismo nombre. Métricas sintéticas no demuestran comprensión semántica ni despliegue en producción.
