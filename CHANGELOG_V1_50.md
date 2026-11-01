# Proyecto Aranza v1.50

## Evaluación comparativa más estricta

- El comparador de benchmarks ahora calcula macro-promedios de precisión, recall y F1 sobre los casos emparejados.
- Cada promedio incluye valor de línea base, valor candidato y diferencia absoluta.
- Si no hay casos emparejados, las métricas agregadas se informan como `null`, evitando presentar ceros engañosos.
- Se agrega `case_sets_match` para indicar si ambas versiones tienen exactamente los mismos nombres de caso.
- Se agrega `--require-same-cases`: la CLI devuelve código 1 si los conjuntos difieren, útil como puerta de control en integración continua.
- Se mantiene el aviso de que los casos ausentes no equivalen a una mejora.

## Ejemplo

```bash
python comparar_benchmarks_memoria.py baseline.json candidato.json --threshold 0.05 --require-same-cases --output comparacion.json
```

## Límites

Los macro-promedios dan el mismo peso a cada caso y pueden ocultar variaciones individuales; revisar siempre `comparisons` y `regressions`. Las métricas dependen de etiquetas de relevancia, y no prueban comprensión semántica general.
