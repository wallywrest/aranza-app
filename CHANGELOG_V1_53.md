# Proyecto Aranza v1.53

## Ejecutor reproducible de benchmarks de memoria

- Se añade `ejecutar_benchmark_memoria.py`, que ejecuta escenarios supervisados contra el endpoint real `/memory/context-evaluate`.
- Usa una base SQLite temporal, aislada de la base habitual de Aranza, y no llama a proveedores externos.
- Produce métricas por escenario compatibles con `comparar_benchmarks_memoria.py`.
- Genera automáticamente fingerprints SHA-256 deterministas a partir de la definición canónica de cada escenario.
- Permite usar escenarios integrados o un manifiesto JSON propio.
- Incluye validación estricta de nombres, consultas, textos relevantes/irrelevantes, límites y opciones.

## Uso

```bash
python ejecutar_benchmark_memoria.py --output benchmark.json
python comparar_benchmarks_memoria.py baseline.json benchmark.json --require-same-cases --require-case-fingerprints --output comparacion.json
```

Manifiesto opcional: objeto JSON con `cases`, cada caso con `name`, `query`, `relevant` (lista de textos), y opcionalmente `irrelevant`, `category`, `limit` y `archive_relevant`.

## Limitaciones

Las etiquetas de relevancia son datos de referencia proporcionados por personas; las métricas evalúan recuperación, no comprensión semántica ni veracidad. Los fingerprints cambian cuando cambia cualquier campo del escenario normalizado. La base temporal se elimina al terminar.

## Validación local

- `python -m pytest -q`: 161 pruebas aprobadas.
- `python -m py_compile main.py ejecutar_benchmark_memoria.py comparar_benchmarks_memoria.py`: correcto.
- Ejecución del benchmark integrado: 4 escenarios generaron informe JSON.
- Sintaxis JavaScript e integridad del ZIP: verificadas antes de empaquetar.
