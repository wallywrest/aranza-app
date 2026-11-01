# Proyecto Aranza v1.15

## Objetivo
Conectar el endpoint de análisis de archivos (v1.14) con la interfaz del chat.

## Cambios
- Añadido botón para adjuntar archivos en el compositor.
- Tipos admitidos en el selector: TXT, MD, CSV, JSON y PDF.
- El usuario puede escribir una instrucción opcional; si no escribe ninguna, se usa el resumen predeterminado del backend.
- Envío multipart autenticado al endpoint `/tools/analyze-file`.
- `apiFetch` reconoce `FormData` y no fija `Content-Type`, para que el navegador genere correctamente el boundary multipart.
- Muestra nombre y tamaño aproximado del archivo seleccionado.
- Actualizada la versión de FastAPI a `1.15.0`.

## Privacidad y límites
- El backend conserva el límite de 5 MB y los formatos permitidos.
- El archivo se procesa en memoria y no se guarda en el servidor ni en el historial remoto.
- La interfaz sí guarda localmente el mensaje que incluye el nombre del archivo y la respuesta de análisis, igual que otros mensajes de conversación.
- Los PDF escaneados sin capa de texto requieren OCR, que todavía no está incluido.
- El análisis necesita un modelo/proveedor configurado y puede generar costos externos.

## Validación
- Suite local: 46 pruebas aprobadas.
- Sintaxis Python validada.
- Sintaxis JavaScript del script de la página validada con Node.js.
- No se hicieron llamadas reales a proveedores ni despliegue en producción.
