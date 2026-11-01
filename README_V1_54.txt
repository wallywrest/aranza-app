PROYECTO ARANZA v1.54

Novedad: métricas estratificadas por grupo en el benchmark de recuperación de memoria.

Ejecutar escenarios integrados:
python ejecutar_benchmark_memoria.py --output benchmark.json

Cada escenario puede incluir `group` para agrupar tipos de evaluación. Si se omite, se usa `general`. El informe incluye métricas por caso y un resumen por grupo con promedios macro de precisión, recall y F1, además de totales de recuerdos omitidos e inesperados.

Los escenarios integrados ahora incluyen recuperación directa, normalización, contexto de proyecto, recuerdos archivados, múltiples recuerdos relevantes y distractores de tema cercano.

Las métricas dependen de etiquetas humanas y no prueban comprensión semántica ni veracidad. Revisa siempre resultados individuales, porque los promedios pueden ocultar fallos particulares.
