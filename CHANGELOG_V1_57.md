# Proyecto Aranza v1.57

- Añade `render.yaml` como plantilla de despliegue con disco persistente montado en `/var/data`.
- Configura el arranque Uvicorn mediante `$PORT` y health check en `/health`.
- Marca contraseña, origen permitido y clave de proveedor como variables que deben configurarse en el panel, no en el repositorio.
- El verificador previo al despliegue ahora exige que `ARANZA_DB_PATH` apunte al disco persistente `/var/data`.
- Añade pruebas para rutas de base de datos relativas y rutas en el disco persistente.

La plantilla no publica la aplicación ni crea secretos fuera del proceso de configuración de Render. Revisa el plan y el coste del disco antes de crear el servicio.
