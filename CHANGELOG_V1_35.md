# Proyecto Aranza v1.35

## Memoria contextual con menos redundancia

- La selección contextual elimina recuerdos con contenido idéntico tras normalizar mayúsculas y acentos.
- También descarta candidatos con alta similitud léxica (Jaccard >= 0.82) para reducir repeticiones en el prompt.
- Se conserva el orden de relevancia: si dos recuerdos se parecen, se prioriza el que ya obtuvo mejor puntuación.
- La deduplicación también se aplica al pequeño conjunto de respaldo para consultas sin coincidencias.
- Los recuerdos archivados siguen excluidos del contexto automático.
- Se añadieron pruebas para duplicados exactos, casi duplicados y exclusión de recuerdos archivados.

## Límites conocidos

La comparación es léxica y local, no semántica. Dos recuerdos redactados de forma muy distinta pueden expresar lo mismo y no detectarse; a la inversa, dos frases cortas similares podrían colapsarse. No requiere servicios externos ni dependencias nuevas.
