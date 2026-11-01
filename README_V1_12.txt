PROYECTO ARANZA v1.12 - NÚCLEO DE MODELOS DESACOPLADO

NOVEDADES
- La lógica del chat ya no está atada directamente al SDK de Groq.
- Se agregó modelos.py con una interfaz HTTP compatible con OpenAI Chat Completions.
- Se pueden configurar proveedor principal y respaldo por separado.
- Si el principal falla, Aranza intenta el respaldo configurado.
- El endpoint /chat informa qué proveedor/modelo respondió; /health no revela claves.
- Se mantienen GROQ_API_KEY y GROQ_MODEL para facilitar la transición.

CONFIGURACIÓN OPCIONAL
ARANZA_PRIMARY_PROVIDER=groq
ARANZA_PRIMARY_BASE_URL=https://api.groq.com/openai/v1
ARANZA_PRIMARY_API_KEY= (si está vacío, usa GROQ_API_KEY)
ARANZA_PRIMARY_MODEL= (si está vacío, usa GROQ_MODEL)
ARANZA_FALLBACK_PROVIDER=groq
ARANZA_FALLBACK_BASE_URL=https://api.groq.com/openai/v1
ARANZA_FALLBACK_API_KEY= (si está vacío, usa GROQ_API_KEY)
ARANZA_FALLBACK_MODEL=llama-3.1-8b-instant
ARANZA_MODEL_TIMEOUT_SECONDS=45

Para usar un proveedor distinto, configura su URL base compatible, clave y modelo. Guarda las claves solo en variables de entorno o secretos del hosting, nunca en index.html ni en el repositorio.

VALIDACIÓN LOCAL
- Sintaxis Python validada.
- 34 pruebas aprobadas.
- Las llamadas HTTP a modelos se simularon; no se consumieron llamadas de API reales.

INSTALACIÓN FUTURA
1. Conserva las versiones anteriores.
2. Haz copia de seguridad de SQLite y del archivo .env.
3. Incluye main.py, modelos.py, index.html, requirements.txt y los demás archivos de la versión.
4. Instala dependencias desde requirements.txt y ejecuta: python -m pytest -q
5. Prueba primero con una copia del entorno real.

LÍMITES
Esta versión crea una capa de proveedores y respaldo. Todavía no es un coordinador inteligente multiagente y no está desplegada en producción.
