# Proyecto Aranza v1.40

## Contexto de revisiones previas de memoria

- La comprobación de similitud ahora consulta las decisiones de revisión guardadas para la misma cuenta.
- Una decisión previa solo se muestra cuando corresponde al mismo recuerdo y la propuesta nueva tiene similitud léxica alta (Jaccard >= 0.65) con la propuesta revisada.
- Se muestra la decisión más reciente por recuerdo, sin eliminar candidatos ni imponer un resultado automático.
- La interfaz indica que una revisión previa es contexto histórico, no un veredicto definitivo.
- Se añadieron pruebas de anotación correcta, aislamiento entre cuentas y omisión de revisiones poco similares.

## Límites

La similitud se calcula por coincidencia de palabras, no por comprensión semántica. Las revisiones no modifican por sí solas los recuerdos ni desactivan futuras alertas.
