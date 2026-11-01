# Proyecto Aranza v1.49

## Comparador de benchmarks de memoria

- Se agrega `comparar_benchmarks_memoria.py`, herramienta offline para comparar dos informes JSON de métricas.
- Compara precisión, recall y F1 por nombre de caso, calcula deltas y señala regresiones superiores al umbral configurado (por defecto 0.05).
- Informa de casos que aparecen solo en la línea base o solo en la versión candidata; no los interpreta como mejoras.
- Valida estructura JSON, nombres únicos, métricas finitas en el rango 0..1 y umbral válido.
- Código de salida: `0` sin regresiones detectadas, `1` si detecta regresiones, `2` si el informe o los argumentos son inválidos.
- No accede a la base de datos de Aranza ni llama a proveedores externos.

## Uso

```bash
python comparar_benchmarks_memoria.py baseline.json candidato.json --threshold 0.05 --output comparacion.json
```

Cada archivo debe tener un objeto JSON con `cases`, una lista de objetos con `name`, `precision`, `recall` y `f1`.

## Límites

Solo compara los casos con el mismo nombre. La ausencia de casos en una versión requiere revisión manual. Las métricas dependen de etiquetas de relevancia y no prueban comprensión semántica general.
