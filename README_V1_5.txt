PROYECTO ARANZA - PAQUETE DE DESARROLLO V1.5

CONTENIDO
- main.py: backend FastAPI actualizado.
- index.html: cliente web de la versión de desarrollo.
- backup_db.py: creación, integridad y restauración de respaldos SQLite.
- requirements.txt: dependencias de ejecución.
- test_*.py y conftest.py: pruebas locales sin llamadas a proveedores externos.
- CHANGELOG_V1_2.md a CHANGELOG_V1_5.md: historial de cambios.

NUEVO EN V1.5
- Exportación JSON autenticada mediante GET /export.
- Guardado transaccional de pregunta y respuesta.
- Corrección del guardado de memorias: contenido y categoría ya no se intercambian.

VALIDACIÓN
- python -m py_compile main.py backup_db.py
- python -m pytest -q
- Última ejecución: 11 pruebas aprobadas.

IMPORTANTE
Este paquete no está desplegado en ningún servidor. No reemplaces archivos de producción sin respaldo y sin verificar variables de entorno y ruta persistente de SQLite.
La aplicación sigue usando una contraseña compartida configurada mediante ARANZA_PASSWORD; todavía no es multiusuario.
Los recuerdos creados en versiones anteriores podrían tener contenido/categoría invertidos. La versión no modifica esos registros automáticamente.
El endpoint /export entrega datos personales en texto legible. Trata el archivo descargado como información privada.
