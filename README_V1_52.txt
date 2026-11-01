PROYECTO ARANZA v1.52

Mejora: el comparador de benchmarks puede detectar si un caso con el mismo nombre cambió de definición, siempre que los informes incluyan un campo fingerprint estable.

Ejemplo de caso en JSON:
{"name":"consulta_ingles","precision":1.0,"recall":0.9,"f1":0.9474,"fingerprint":"sha256:..."}

Uso estricto:
python comparar_benchmarks_memoria.py baseline.json candidato.json --require-same-cases --require-case-fingerprints --output comparacion.json

El modo estricto falla con código 1 si cambian los conjuntos de casos o si faltan/cambian fingerprints en los casos emparejados. El código 2 indica error de entrada o de escritura.

Los informes previos siguen funcionando sin fingerprints si no se activa el modo estricto. Para una comparación fiable, los fingerprints deben calcularse desde una representación canónica de la consulta, referencias y configuración del escenario.
