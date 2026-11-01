# Proyecto Aranza v1.51

## Detección de regresiones agregadas

- El comparador ahora detecta caídas en macro-promedios incluso si cada caso individual cae menos que el umbral.
- Los informes incluyen `aggregate_regressions` y `aggregate_regression_count` para distinguir regresiones por caso de regresiones agregadas.
- El umbral agregado es configurable con `--aggregate-threshold`; por defecto es la mitad del umbral por caso.
- El estado global y el código de salida de la CLI consideran ambos tipos de regresión.
- Se conservan las comparaciones por caso y las alertas por conjuntos de casos distintos.

## Motivo

Una regresión pequeña repetida en muchos escenarios puede degradar el comportamiento global sin que ningún escenario individual supere el umbral. Esta versión evita que ese patrón aparezca como un resultado completamente satisfactorio.

## Límites

Las métricas dependen de los informes y etiquetas de referencia; el comparador no demuestra comprensión semántica ni calidad general de Aranza. Los informes deben proceder de pruebas comparables.
