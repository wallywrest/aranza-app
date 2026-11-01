# Proyecto Aranza v1.46

## Auditoría heurística del contexto recuperado

- Añade `GET /memory/context-audit?query=...&limit=8` para evaluar señales léxicas del contexto seleccionado por el recuperador existente.
- Devuelve cobertura léxica aproximada, cantidad de palabras clave, advertencias de cobertura baja/parcial y pares de recuerdos potencialmente redundantes.
- Las señales de redundancia solo son indicios basados en coincidencia de palabras; no afirman equivalencia semántica ni verdad.
- La consulta se limita a la cuenta autenticada, admite hasta 4.000 caracteres y limita resultados a 1–20 recuerdos.
- No llama a modelos externos, no guarda el texto de consulta en el historial y no modifica recuerdos.

## Validación

- Pruebas nuevas para cobertura, ausencia de efectos secundarios, aislamiento entre cuentas y límites de entrada.
- Ejecutar `python -m pytest -q` para repetir toda la suite.
