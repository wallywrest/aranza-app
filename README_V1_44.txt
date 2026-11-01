Proyecto Aranza v1.44

Novedad: endpoint de solo lectura GET /memory/relations.

Genera pares de recuerdos con coincidencias léxicas y los clasifica como posible relación, posible duplicado o posible contradicción usando los patrones existentes. Devuelve IDs, contenido, categoría, similitud aproximada y una nota de cautela.

La consulta solo usa recuerdos de la cuenta autenticada. No modifica, combina ni elimina recuerdos. La detección es heurística y puede omitir relaciones semánticas o marcar similitudes que no sean importantes.

Validación local: 116 pruebas aprobadas y compilación Python correcta. El parche no está desplegado en producción ni ha sido probado con proveedores externos.

Integra este parche en la futura versión consolidada; no es necesario instalar versiones intermedias por separado.
