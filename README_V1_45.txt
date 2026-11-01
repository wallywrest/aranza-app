PROYECTO ARANZA v1.45

Novedad: previsualización del contexto de memoria.

Endpoint autenticado:
GET /memory/context-preview?query=texto&limit=8

Permite ver los recuerdos que el selector actual considera para una consulta, junto con términos coincidentes y una puntuación léxica aproximada. No llama a un modelo, no guarda la consulta y no modifica recuerdos. La respuesta solo contiene recuerdos de la cuenta autenticada.

La puntuación usa coincidencia de palabras y no representa comprensión semántica. El endpoint no está conectado a un proveedor externo ni equivale a una evaluación humana de relevancia.

Consulta CHANGELOG_V1_45.md para más detalles. Configura secretos y proveedor mediante las instrucciones generales del proyecto antes de ejecutar la aplicación.
