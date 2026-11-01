# Antes de publicar Aranza en GitHub y Render

Esta guía prepara el despliegue, pero no publica nada ni crea servicios.

## 1. Antes de subir a GitHub
- Sube solo el código y archivos de configuración de ejemplo.
- No subas `.env`, contraseñas, claves API, tokens, ni `aranza.sqlite3`.
- Confirma que `.gitignore` cubra `.env`, bases SQLite y archivos de respaldo.
- Mantén el ZIP como respaldo local; no lo uses como sustituto del control de versiones.

## 2. Servicio web
- Comando de inicio típico: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Health check: `/health`.
- Variables secretas: `ARANZA_PASSWORD`, `ARANZA_SESSION_SECRET`, `GROQ_API_KEY`.
- `ARANZA_ALLOWED_ORIGINS` debe contener el origen HTTPS exacto desde el que se sirve la interfaz.

## 3. Persistencia: condición que bloquea un lanzamiento con memoria real
Aranza guarda conversaciones, sesiones y recuerdos en SQLite. El disco local de un servicio web puede ser efímero; si se reinicia o redepliega, los datos podrían perderse. Antes de usarla con datos reales, hay que configurar almacenamiento persistente compatible y apuntar `ARANZA_DB_PATH` a esa ruta, o diseñar y probar otra base de datos. No publicar recuerdos reales hasta validar esto.

## 4. Comprobación local
Ejecuta `python preparar_despliegue.py` después de definir las variables de entorno. El script valida configuración básica; no prueba Render, DNS, persistencia real ni conectividad externa.

## 5. Verificación final
Ejecuta `python -m pytest -q`, `python -m py_compile main.py preparar_despliegue.py` y `python ejecutar_benchmark_memoria.py`. Revisa `/health` tras desplegar y confirma login, reinicio con persistencia, cambio de contraseña y restauración de respaldo antes de cargar datos importantes.

**Estado:** listo para preparación de repositorio y pruebas controladas; no declarar producción lista hasta validar persistencia y recuperación de respaldos.
