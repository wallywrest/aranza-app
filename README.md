# Aranza · versión mejorada

Proyecto FastAPI + Groq con interfaz web. Se conservan el gato original, el nombre **Aranza**, la tipografía del nombre y la paleta azul/periwinkle y naranja.

## Qué mejora

- El historial del servidor genera títulos automáticos usando el primer mensaje del usuario.
- Al abrir una conversación se recuperan sus mensajes reales desde SQLite, no solo desde el almacenamiento local del navegador.
- Eliminar una conversación elimina sus mensajes del servidor y del caché local, después de confirmar.
- Se muestra el estado de conexión y si falta configurar `GROQ_API_KEY`.
- El perfil conversacional de Aranza ahora pide variar el ritmo y distinguir entre charla casual, desahogo, análisis y ayuda práctica.
- Puedes proteger los endpoints privados con `ARANZA_ACCESS_TOKEN`.
- El renderizado de respuestas mantiene el escape de HTML para evitar que contenido del modelo se interprete como HTML arbitrario.

## Ejecución local

1. Instala Python 3.10 o superior.
2. Crea un entorno virtual y activa el entorno.
3. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Copia `.env.example` a `.env` y coloca tu clave de Groq en `GROQ_API_KEY`.
5. Ejecuta:

   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

6. Abre `http://127.0.0.1:8000`.

## Publicación en Render

- Usa un servicio **Web Service** con el repositorio que contiene estos archivos.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Configura `GROQ_API_KEY` en Environment Variables de Render. Nunca subas la clave al repositorio.
- Configura también `ARANZA_ACCESS_TOKEN` con una clave larga y privada. Al abrir Aranza, el navegador pedirá esa clave y la guardará en `sessionStorage` durante la sesión del navegador.
- Si el plan de alojamiento permite un disco persistente, móntalo, por ejemplo, en `/var/data` y define `ARANZA_DB_PATH=/var/data/aranza.sqlite3`. Sin disco persistente, SQLite puede perderse al reiniciar o redeplegar el servicio.

## Privacidad

Si `ARANZA_ACCESS_TOKEN` está vacío, los endpoints de chat, historial y memoria quedan sin autenticación. No publiques la aplicación con conversaciones personales sin configurar esa variable. La clave de acceso protege los endpoints, pero no sustituye una cuenta individual por usuario: la base de datos sigue siendo compartida por esta instalación.

## Archivos

- `main.py`: API, instrucciones de personalidad, SQLite y endpoints.
- `index.html`: interfaz completa.
- `requirements.txt`: dependencias.
- `.env.example`: variables de entorno de ejemplo.
