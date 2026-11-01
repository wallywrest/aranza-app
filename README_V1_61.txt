PROYECTO ARANZA v1.61

Cambios:
- Validación de sesiones más estricta: cuenta y vencimiento del token deben coincidir con el registro persistente.
- Pruebas para tokens inconsistentes y plantilla de despliegue.
- Render solicita configurar ARANZA_USERNAME explícitamente en vez de usar "owner" por defecto.

Ejecutar pruebas:
  python -m pytest -q

Revisar configuración antes del despliegue:
  python preparar_despliegue.py

La validación local no equivale a una publicación real. No subas contraseñas, claves API ni secretos al repositorio.
