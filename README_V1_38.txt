PROYECTO ARANZA v1.38

Novedad: flujo de revisión para posibles contradicciones.

En la comprobación previa al guardado, las coincidencias clasificadas como posibles contradicciones permiten:
- señalarlas como posible cambio temporal durante la revisión;
- descartar la clasificación como falsa alarma en la vista actual;
- archivar el recuerdo anterior tras una confirmación explícita.

Archivar no borra el recuerdo; lo excluye del contexto automático y permite reactivarlo. Las dos primeras acciones no se guardan de forma persistente. La detección es heurística, no semántica.

Validación local:
- Python: compilación correcta.
- Pruebas automatizadas: 98 aprobadas.
- JavaScript: sintaxis comprobada con Node.js.
- ZIP: se verifica su integridad después de generarse.

No desplegado ni validado de extremo a extremo con un proveedor real de IA.
