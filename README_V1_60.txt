PROYECTO ARANZA v1.60

Esta versión refuerza el verificador previo al despliegue:
- Clave de sesión separada de la contraseña y sin valores de ejemplo.
- Orígenes HTTPS exactos, únicos y sin rutas.
- Advertencia por nombre de usuario predeterminado.

Ejecutar pruebas:
  python -m pytest -q

Revisar configuración:
  python preparar_despliegue.py

El verificador no publica la aplicación ni sustituye las pruebas reales en Render. Configura los secretos desde el panel del proveedor y no los subas a GitHub.
