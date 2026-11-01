PROYECTO ARANZA v1.23

CAMBIO PRINCIPAL
La memoria personal ahora se selecciona según la relevancia léxica con el mensaje actual, en vez de enviar automáticamente todos los recuerdos recientes al modelo.

LÍMITES
- Chat: hasta 8 recuerdos relevantes.
- Análisis de archivos: hasta 5 recuerdos relevantes.
- Sin coincidencias claras: se usa un conjunto pequeño de preferencias/proyectos o recuerdos recientes.
- La selección es local y no requiere embeddings ni llamadas externas.

INSTALACIÓN FUTURA
No sustituir archivos en producción sin copia de seguridad de SQLite y validación de migraciones. Esta versión no se ha desplegado en un servidor real.

VALIDACIÓN
68 pruebas automatizadas aprobadas localmente. main.py pasó py_compile.
