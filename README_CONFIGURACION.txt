ARANZA: ARCHIVOS COORDINADOS CON ACCESO PRIVADO

Archivos incluidos
- main.py: backend FastAPI con autenticación por contraseña y token temporal firmado.
- index.html: interfaz con pantalla de acceso, conserva el SVG original del gato y usa un lobo para el avatar del usuario.
- requirements.txt: dependencias.
- render_env.example.txt: guía de variables secretas para Render.

CONFIGURACIÓN EN RENDER
1. En Render > tu servicio > Environment, configura:
   - GROQ_API_KEY: tu clave actual de Groq.
   - ARANZA_PASSWORD: contraseña inicial para crear la primera cuenta. No la escribas en el HTML ni en GitHub. Después de crear la cuenta, la contraseña guardada en SQLite es la autoridad.
   - ARANZA_SESSION_SECRET: una clave aleatoria larga, distinta del PIN (mínimo 32 caracteres).
   - GROQ_MODEL: openai/gpt-oss-120b (o el modelo que ya tengas funcionando).
2. Conserva el comando de inicio de tu servicio. Normalmente: uvicorn main:app --host 0.0.0.0 --port $PORT
3. Despliega ambos archivos juntos. No publiques .env, aranza.sqlite3 ni secretos.

SEGURIDAD
- /login y /health son públicos; /session, /chat, /memory y /conversations requieren un token válido.
- El token de sesión se guarda en sessionStorage y vence según ARANZA_SESSION_TTL_SECONDS (por defecto, 12 horas).
- Los intentos fallidos recientes se guardan en SQLite, por lo que reiniciar el proceso no borra el límite. En despliegues con varias instancias, el almacenamiento debe ser compartido y coordinado para que la protección sea consistente.
- Usa una contraseña larga y única. El límite de intentos ayuda, pero no sustituye una contraseña robusta. Mantén los secretos fuera de GitHub.

DATOS Y SINCRONIZACIÓN
El historial y la memoria siguen en SQLite del servidor. Para conservarlos tras reinicios/despliegues de Render, configura un disco persistente y apunta ARANZA_DB_PATH a su ruta de montaje. El HTML mantiene localStorage solo como respaldo y metadatos locales.


RESPALDOS Y RESTAURACIÓN (v1.3)
- La base usa SQLite en modo WAL y espera hasta 10 segundos ante bloqueos breves.
- Configura ARANZA_DB_PATH en un disco persistente del proveedor; WAL no sustituye al almacenamiento persistente.
- Crea un respaldo verificado con: python backup_db.py backup
- Para elegir carpeta: python backup_db.py backup --output-dir ./respaldos
- Para restaurar: detén el servicio y ejecuta python backup_db.py restore --source RUTA_DEL_RESPALDO --confirm
- Antes de restaurar, el script crea automáticamente una copia de la base actual en backups_pre_restore.
- Guarda una copia adicional fuera del servidor. Un respaldo guardado únicamente junto a la app puede desaparecer con el mismo disco que debía salvarte.
- Prueba periódicamente la restauración en una copia de prueba. Crear respaldos sin probarlos es básicamente coleccionar esperanza.

ALCANCE DE ESTA VERSIÓN
Esta versión sigue usando una sola contraseña compartida configurada en el servidor. No es multiusuario: las conversaciones y memorias pertenecen al espacio de esa instancia. No publiques el servicio como multiusuario sin implementar cuentas, propiedad de datos y autorización por usuario.


CONTROL DE INTENTOS (v1.4)
Los intentos fallidos se registran en la tabla `intentos_login` de SQLite y se eliminan al vencer la ventana o tras un inicio de sesión correcto. Esto evita que reiniciar el proceso borre inmediatamente el límite. En múltiples instancias, asegúrate de que todas usan el mismo almacenamiento compartido compatible con SQLite; no uses un disco local independiente por instancia.

ARANZA v1.8
- ARANZA_USERNAME: nombre de usuario de acceso (por defecto: owner).
- El acceso solicita usuario y contraseña.
- La tabla de cuentas almacena un hash PBKDF2-HMAC-SHA256 con salt, no la contraseña en texto plano.
- Sigue siendo una instancia de una sola cuenta; no existe registro público ni recuperación por correo. Desde v1.9 puedes cambiar la contraseña en el menú lateral.


SEGURIDAD DE CUENTA (v1.9)
- Puedes cambiar la contraseña desde el menú lateral de Aranza.
- Se requiere la contraseña actual y una nueva de al menos 12 caracteres.
- Al cambiarla se revocan todas las sesiones activas; inicia sesión de nuevo.
- Conserva la base SQLite y sus copias de seguridad: ahí se almacena el hash de la contraseña y la información persistente.

ARANZA v1.9
- El cambio de contraseña requiere la contraseña actual y al menos 12 caracteres para la nueva.
- Todas las sesiones se revocan después del cambio.
- ARANZA_PASSWORD inicializa la primera cuenta y no sobrescribe la contraseña después de reiniciar.
\n\nAranza v1.62: se añadieron pruebas de persistencia tras reinicializar SQLite, reapertura de conexiones y respaldo de datos WAL. Consultar CHANGELOG_V1_62.md.\n
Aranza v1.63: la restauración elimina los archivos laterales WAL/SHM obsoletos tras crear la copia preventiva. Ver CHANGELOG_V1_63.md.
