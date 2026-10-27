ARANZA: ARCHIVOS COORDINADOS CON ACCESO PRIVADO

Archivos incluidos
- main.py: backend FastAPI con autenticación por contraseña y token temporal firmado.
- index.html: interfaz con pantalla de acceso, conserva el SVG original del gato y usa un lobo para el avatar del usuario.
- requirements.txt: dependencias.
- render_env.example.txt: guía de variables secretas para Render.

CONFIGURACIÓN EN RENDER
1. En Render > tu servicio > Environment, configura:
   - GROQ_API_KEY: tu clave actual de Groq.
   - ARANZA_PASSWORD: tu PIN privado de seis dígitos. No lo escribas en el HTML ni en GitHub.
   - ARANZA_SESSION_SECRET: una clave aleatoria larga, distinta del PIN (mínimo 32 caracteres).
   - GROQ_MODEL: openai/gpt-oss-120b (o el modelo que ya tengas funcionando).
2. Conserva el comando de inicio de tu servicio. Normalmente: uvicorn main:app --host 0.0.0.0 --port $PORT
3. Despliega ambos archivos juntos. No publiques .env, aranza.sqlite3 ni secretos.

SEGURIDAD
- /login y /health son públicos; /session, /chat, /memory y /conversations requieren un token válido.
- El token de sesión se guarda en sessionStorage y vence según ARANZA_SESSION_TTL_SECONDS (por defecto, 12 horas).
- Hay un límite básico de intentos fallidos en memoria por dirección cliente. En despliegues con varias instancias conviene usar un limitador compartido.
- Un PIN de seis dígitos es cómodo pero tiene poca entropía. El límite de intentos reduce el riesgo, pero no sustituye una contraseña larga si el servicio guarda datos muy sensibles.
- El limitador en memoria se reinicia cuando el proceso se reinicia. Mantén secretos fuera de GitHub.

DATOS Y SINCRONIZACIÓN
El historial y la memoria siguen en SQLite del servidor. Para conservarlos tras reinicios/despliegues de Render, configura un disco persistente y apunta ARANZA_DB_PATH a su ruta de montaje. El HTML mantiene localStorage solo como respaldo y metadatos locales.
