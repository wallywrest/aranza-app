PROYECTO ARANZA v1.53

Novedad: ejecutor reproducible de benchmarks supervisados de memoria.

Ejecutar escenarios integrados:
python ejecutar_benchmark_memoria.py --output benchmark.json

Comparar el resultado con una referencia:
python comparar_benchmarks_memoria.py baseline.json benchmark.json --require-same-cases --require-case-fingerprints --output comparacion.json

También puedes proporcionar un manifiesto JSON con una lista "cases". Cada caso necesita "name", "query" y "relevant" (lista de textos). Opcionales: "irrelevant", "category", "limit" y "archive_relevant".

El ejecutor usa una base SQLite temporal y no llama a proveedores externos. Produce fingerprints SHA-256 estables de la definición de cada escenario. Los resultados dependen de las etiquetas humanas y evalúan recuperación, no comprensión ni verdad.

Validación local: 161 pruebas aprobadas; compilación Python correcta; benchmark integrado de 4 escenarios ejecutado.
