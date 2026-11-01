# Aranza v1.79

## Adjuntos múltiples en una misma consulta

- El selector de archivos permite elegir hasta cinco adjuntos por mensaje.
- La interfaz valida antes del envío el máximo de cinco archivos y el límite individual de 5 MiB.
- Los archivos se procesan secuencialmente mediante los endpoints autenticados ya existentes (`/tools/analyze-file` y `/tools/analyze-image`). No se modifican contratos ni rutas del backend.
- La respuesta reúne los resultados por nombre de archivo.
- Los archivos continúan procesándose en memoria; no se guardan en SQLite ni se envían automáticamente al recuperar conexión.

Cada archivo sigue sujeto a las validaciones de tipo, contenido y tamaño del backend. Los análisis visuales siguen requiriendo un proveedor multimodal configurado. La selección múltiple no equivale a un análisis conjunto: cada adjunto se analiza por separado y luego se presentan los resultados en una respuesta agrupada.
