# Aranza v1.12

## Núcleo de modelos desacoplado
- Se añadió `modelos.py`, un enrutador de modelos que usa el formato HTTP de chat completions compatible con OpenAI.
- La ruta `/chat` ya no depende directamente del SDK de Groq.
- El proveedor principal y el respaldo se configuran por variables de entorno.
- Se puede configurar un proveedor compatible diferente como respaldo, con URL y clave propias.
- Si un proveedor falla, Aranza intenta el siguiente y evita exponer detalles sensibles del proveedor al usuario.
- La respuesta del endpoint de chat incluye el proveedor y el modelo que respondieron.
- El endpoint `/health` indica si existe al menos un proveedor configurado, sin exponer claves.
- Se reemplazaron pruebas que dependían del SDK anterior por pruebas simuladas del nuevo enrutador.

## Configuración
Variables principales compatibles con la configuración anterior:
- `GROQ_API_KEY`
- `GROQ_MODEL`

Variables nuevas opcionales:
- `ARANZA_PRIMARY_PROVIDER` (por defecto `groq`)
- `ARANZA_PRIMARY_BASE_URL` (por defecto `https://api.groq.com/openai/v1`)
- `ARANZA_PRIMARY_API_KEY` (si no se define, usa `GROQ_API_KEY`)
- `ARANZA_PRIMARY_MODEL` (si no se define, usa `GROQ_MODEL`)
- `ARANZA_FALLBACK_PROVIDER`
- `ARANZA_FALLBACK_BASE_URL`
- `ARANZA_FALLBACK_API_KEY` (si no se define, usa `GROQ_API_KEY`)
- `ARANZA_FALLBACK_MODEL` (por defecto `llama-3.1-8b-instant`)
- `ARANZA_MODEL_TIMEOUT_SECONDS` (por defecto 45)

Los proveedores deben aceptar el formato HTTP `/chat/completions` compatible con OpenAI. No todos los proveedores ni todos sus modelos son compatibles de forma idéntica; se debe validar cada configuración.

## Validación
- `python -m py_compile main.py modelos.py`
- `python -m pytest -q`: 34 pruebas aprobadas.
- Las llamadas de proveedor se simularon en pruebas; no se consumieron llamadas de API reales.

## Límites
- Esto es una capa de enrutamiento y respaldo, no una orquestación inteligente de múltiples agentes todavía.
- El sistema intenta proveedores en orden; aún no clasifica automáticamente tareas ni compara respuestas de modelos.
- No está desplegada en producción.
