# Proyecto Aranza v1.38

## Resolución asistida de posibles contradicciones
- En los candidatos marcados como posibles contradicciones, la interfaz ofrece tres acciones de revisión.
- «Puede ser un cambio temporal» etiqueta el candidato solo durante la revisión actual; no altera la memoria ni guarda una etiqueta persistente.
- «No es contradicción» descarta el candidato de la vista actual sin alterar datos.
- «Archivar recuerdo anterior» requiere confirmación explícita y utiliza la ruta autenticada de archivado existente. El recuerdo se conserva y puede reactivarse.
- Las acciones de revisión se crean con APIs DOM y `textContent`, sin interpolar contenido del recuerdo como HTML.

## Límites
La detección sigue siendo heurística léxica. No se implementa resolución automática ni historial persistente de decisiones de revisión.
