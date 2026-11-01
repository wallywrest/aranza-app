# Proyecto Aranza v1.44

## Relaciones heurísticas entre recuerdos

- Añade `GET /memory/relations`, una consulta de solo lectura que busca pares de recuerdos relacionados mediante las reglas léxicas existentes.
- Cada relación incluye los dos recuerdos, tipo de relación sugerido, similitud aproximada y coincidencia de categoría.
- El resultado está limitado a 1–200 relaciones por consulta; el análisis parte de hasta 500 recuerdos de la cuenta autenticada.
- Las relaciones están aisladas por cuenta y no modifican, fusionan ni eliminan recuerdos.
- La clasificación es heurística y no constituye comprensión semántica ni confirma contradicciones.

## Validación

- `python -m py_compile main.py`: correcto.
- `python -m pytest -q`: 116 pruebas aprobadas.
- Pruebas nuevas: relaciones detectadas, aislamiento entre cuentas, límite de consulta y ausencia de cambios automáticos.

No desplegado en producción ni validado con proveedores de IA externos.
