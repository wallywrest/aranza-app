PROYECTO ARANZA v1.14 - ANÁLISIS TEMPORAL DE ARCHIVOS

NOVEDADES
- Endpoint autenticado POST /tools/analyze-file.
- Formatos: TXT, MD, CSV, JSON y PDF con texto seleccionable.
- Los archivos se procesan en memoria; no se guardan en disco ni se añaden al historial.
- Límites: 5 MiB por archivo, 40 páginas PDF, 45.000 caracteres extraídos y 1.200 caracteres de instrucción.
- El texto del documento se trata como contenido no confiable para reducir riesgos de instrucciones maliciosas incrustadas.
- La respuesta devuelve el análisis, proveedor/modelo, caracteres extraídos y si el texto fue truncado.

USO DE API
1. Inicia sesión y conserva el token de sesión.
2. Envía una solicitud multipart/form-data a POST /tools/analyze-file.
3. Campos: file (archivo requerido) e instruction (opcional).
4. Incluye Authorization: Bearer <token>.

DEPENDENCIAS NUEVAS
- python-multipart
- pypdf
Instálalas con `pip install -r requirements.txt`.

VALIDACIÓN
- 46 pruebas automatizadas aprobadas localmente.
- Sintaxis Python validada.
- No se han hecho llamadas a proveedores reales ni despliegue de producción.

LIMITACIONES
- La interfaz web aún no tiene un botón para subir archivos; esta versión habilita el endpoint de backend.
- No hay OCR para PDF escaneados ni soporte DOCX/XLSX todavía.
- Conserva una copia de seguridad antes de actualizar el entorno real.
