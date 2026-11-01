PROYECTO ARANZA v1.39
Registro persistente de decisiones sobre recuerdos

CONTENIDO
- main.py e index.html actualizados.
- Módulos y pruebas del proyecto.
- CHANGELOG_V1_39.md.

NOVEDAD
Las decisiones de revisión de posibles contradicciones pueden guardarse y consultarse desde el panel de memoria. Las decisiones disponibles son: posible cambio temporal, no es contradicción y recuerdo archivado.

SEGURIDAD
Las rutas requieren sesión autenticada y verifican que el recuerdo pertenezca a la cuenta activa. El historial de decisiones está limitado a las 100 más recientes por cuenta.

ACTUALIZACIÓN
Antes de reemplazar archivos en una instalación existente, realiza una copia de seguridad de la base SQLite y de los archivos actuales. Esta entrega es un parche de código; no despliega ni migra una instalación remota por sí sola.

VALIDACIÓN LOCAL
102 pruebas automatizadas aprobadas. Compilación Python y sintaxis JavaScript comprobadas. No se ha realizado una prueba integral en navegador con un proveedor real de IA.
