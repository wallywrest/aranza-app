# Aranza v1.14

## Análisis temporal de archivos
- Nuevo endpoint autenticado `POST /tools/analyze-file`.
- Admite TXT, Markdown, CSV, JSON y PDF con texto seleccionable.
- El archivo se procesa en memoria y no se guarda en disco ni en el historial.
- Límite de archivo: 5 MiB; máximo de 40 páginas PDF y 45.000 caracteres extraídos.
- Instrucción de análisis limitada a 1.200 caracteres.
- El contenido del archivo se delimita como entrada no confiable para reducir el riesgo de prompt injection.
- Respuesta indica proveedor/modelo, cantidad de caracteres, truncamiento y que el archivo no se guardó.
- Errores claros para formatos no admitidos, archivos vacíos, PDF cifrados/dañados y PDF sin texto extraíble.

## Dependencias
- `python-multipart` para cargas multipart.
- `pypdf` para extraer texto de PDF.

## Validación
- 46 pruebas automatizadas aprobadas en entorno local.
- Compilación de Python validada.
- No se realizaron llamadas reales a proveedores ni despliegue de producción.

## Limitaciones
- El endpoint todavía no está conectado a un botón de carga en la interfaz web.
- PDF escaneados requieren OCR, aún no incluido.
- No admite DOCX/XLSX en esta versión.
