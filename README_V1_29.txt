Proyecto Aranza v1.29

Novedad: antes de guardar un recuerdo, la interfaz u otro cliente puede llamar a POST /memory/check con JSON como:
{"content":"Mi meta es estudiar ingeniería industrial","category":"metas"}

Se requiere la autenticación habitual (Bearer token). La respuesta lista candidatos de la cuenta autenticada. Es una comprobación de similitud léxica, no un detector fiable de contradicciones, y no modifica datos automáticamente.

Esta entrega es un parche incremental. No está desplegada ni verificada con proveedores externos reales.
