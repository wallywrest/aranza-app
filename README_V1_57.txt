PROYECTO ARANZA v1.57

Novedad principal: preparación más segura para Render.

- render.yaml monta un disco persistente en /var/data.
- SQLite se configura en /var/data/aranza.sqlite3.
- El servidor inicia con Uvicorn usando el puerto PORT proporcionado por Render.
- /health queda configurado como comprobación de salud.
- ARANZA_PASSWORD, ARANZA_ALLOWED_ORIGINS y GROQ_API_KEY se completan en el panel de Render.

Antes de crear el servicio, revisa el plan/coste de Render y confirma el dominio real del frontend para ARANZA_ALLOWED_ORIGINS. No subas .env, secretos ni bases de datos a GitHub.

Verificación local:
  python preparar_despliegue.py
  python -m pytest -q

Esto no equivale a un despliegue real ni prueba el proveedor remoto.
