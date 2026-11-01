PROYECTO ARANZA v1.50

Novedad: comparación agregada de benchmarks y control estricto de cobertura de casos.

Cambios:
- comparar_benchmarks_memoria.py calcula macro-promedios de precisión, recall y F1 en casos emparejados.
- Informa si los conjuntos de casos coinciden exactamente.
- La opción --require-same-cases hace fallar la evaluación (código 1) cuando faltan o sobran casos.
- Si no hay casos emparejados, los agregados son null y no ceros artificiales.

Ejemplo:
  python comparar_benchmarks_memoria.py baseline.json candidato.json --threshold 0.05 --require-same-cases --output comparacion.json

Validación:
  python -m pytest -q
  python -m py_compile main.py comparar_benchmarks_memoria.py

Los resultados son métricas sobre etiquetas de referencia, no una prueba de comprensión semántica ni de despliegue en producción.
