# v1.88 — Registro de herramientas y ejecución unificada

- Añadido `herramientas.py` con contratos explícitos, lista permitida y validación estricta.
- Añadido `GET /tools/catalog` autenticado, sin secretos ni ejecución.
- Añadido `POST /tools/execute` autenticado para búsqueda, investigación y lectura web de solo lectura.
- Devuelve herramienta, estado, duración y resultado; limita argumentos y rechaza campos desconocidos.
- Análisis de archivos e imágenes permanecen en endpoints multipart dedicados.
- No se permite ejecución arbitraria, operaciones con efectos secundarios ni herramientas no registradas.
- Añadidas pruebas de autenticación, validación, lista permitida y ejecución simulada.
