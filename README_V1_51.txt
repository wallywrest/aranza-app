PROYECTO ARANZA v1.51

Mejora: el comparador de benchmarks detecta tanto regresiones individuales como caídas agregadas en precisión, recall y F1. El umbral agregado por defecto es la mitad del umbral individual y puede configurarse por separado.

Uso:
python comparar_benchmarks_memoria.py baseline.json candidato.json --threshold 0.05 --aggregate-threshold 0.025 --require-same-cases --output comparacion.json

Código de salida:
0 = no se detectaron regresiones según el umbral y la configuración.
1 = se detectaron regresiones o, con --require-same-cases, difieren los conjuntos de casos.
2 = error de entrada o de escritura del informe.

Validar antes de usar los resultados para decisiones de integración. La herramienta compara métricas reportadas; no certifica por sí sola la calidad semántica de la IA.
