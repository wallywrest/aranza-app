# Aranza v1.4: límite de intentos persistente

## Cambios
- Los intentos fallidos de acceso ahora se registran en SQLite, con índice por cliente y fecha.
- Reiniciar el proceso ya no borra los intentos fallidos dentro de la ventana de bloqueo.
- Los intentos antiguos se depuran y un inicio de sesión correcto limpia los intentos del cliente.
- Se añadió una prueba que borra la caché en memoria y verifica que el bloqueo sigue activo.

## Validación local
- `python -m py_compile main.py backup_db.py`
- `python -m pytest -q`
- Resultado: **8 pruebas aprobadas**.

## Límites
- El límite se basa en la IP observada por FastAPI. La configuración de proxy debe verificarse en el despliegue real.
- No es una solución multiusuario y no reemplaza una política de contraseña robusta.
- No se modificó producción ni se verificó el disco persistente del hosting.
