# Aranza v1.101 — Revisión priorizada de auditorías

- Nuevo `informe_auditoria.py`: consume el JSON generado por `auditoria_desarrollo.py`.
- Valida la estructura básica, normaliza severidades y agrupa hallazgos duplicados mediante huellas deterministas.
- Clasifica hallazgos en sintaxis, rutas API, pendientes, informativos u otros.
- Prioriza errores y revisiones antes de observaciones informativas y propone el siguiente paso de revisión humana.
- Genera un resumen JSON y un informe Markdown.
- Es de solo lectura respecto al proyecto auditado: no inspecciona ni edita sus fuentes, no ejecuta código y no aplica correcciones.
- Añade pruebas para deduplicación, prioridad, clasificación, entradas inválidas e informes vacíos.
