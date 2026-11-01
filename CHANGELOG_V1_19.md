# Aranza v1.19

## Lector limitado de páginas públicas
- Nuevo módulo `lector_web.py` y endpoint autenticado `POST /tools/read-webpage`.
- Solo HTTP/HTTPS; rechaza credenciales embebidas, direcciones privadas/reservadas y hosts locales.
- Valida resolución DNS, desactiva redirecciones automáticas y no usa proxies del entorno.
- Solo acepta HTML/XHTML, limita descarga a 1 MB, timeout de 10 s y texto extraído a 12.000 caracteres.
- Extrae título y texto legible; omite scripts, estilos, navegación y contenido de varias etiquetas no esenciales.
- La respuesta advierte que el contenido es no confiable y puede estar incompleto.

## Validación
- `python -m py_compile main.py lector_web.py`
- `python -m pytest -q`: 57 pruebas aprobadas.
- Las pruebas de red usan transportes simulados; no demuestran compatibilidad con todas las páginas reales ni sustituyen una revisión de seguridad de despliegue.

## Limitaciones conocidas
- No sigue redirecciones, no ejecuta JavaScript, no resuelve CAPTCHA ni extrae contenido de páginas que requieren iniciar sesión.
- El chequeo DNS y la conexión HTTP son operaciones separadas; para un despliegue expuesto a usuarios no confiables, se recomienda aislamiento de red o un transporte que fije la IP validada para mitigar DNS rebinding/TOCTOU.
- Esta versión agrega el endpoint de backend; todavía no incorpora un botón de lectura de URL en el chat.
