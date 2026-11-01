# Aranza v1.29

## Detección preventiva de recuerdos similares
- Añadido `POST /memory/check`, protegido por autenticación y limitado a recuerdos de la cuenta activa.
- Añadido análisis léxico local para identificar candidatos a duplicados o recuerdos relacionados antes de guardar uno nuevo.
- El endpoint solo informa candidatos: no modifica, fusiona ni elimina recuerdos automáticamente.
- Incluye puntuación aproximada, categoría, identificador y tipo de revisión sugerido.
- Añadidas pruebas para similitud, textos no relacionados, autenticación y aislamiento entre cuentas.

## Limitaciones
La similitud es heurística léxica y no determina contradicciones semánticas reales. Los resultados requieren revisión humana.
