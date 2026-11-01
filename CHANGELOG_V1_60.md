# Aranza v1.60

## Preflight de seguridad reforzado
- Rechaza secretos de sesión iguales a la contraseña y valores de ejemplo comunes.
- Valida que los orígenes HTTPS sean únicos y no incluyan rutas, parámetros ni fragmentos.
- Advierte si el nombre de usuario conserva valores predeterminados comunes.
- Amplía las pruebas automatizadas de configuración de despliegue.

## Límites
- El preflight solo revisa las variables entregadas; no confirma configuración real del proveedor ni el estado del servicio remoto.
- El nombre de usuario predeterminado genera una advertencia, no bloquea la ejecución.
