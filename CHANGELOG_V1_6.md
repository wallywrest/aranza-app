# Aranza v1.6

## Cambios
- El chequeo del límite de intentos y el registro de contraseñas incorrectas ahora ocurren dentro de una transacción SQLite `BEGIN IMMEDIATE`.
- Esto reduce la condición de carrera donde varias peticiones simultáneas podían leer el mismo contador antes de registrar fallos.
- Un inicio de sesión correcto limpia los intentos anteriores en la misma transacción.
- Se agregaron pruebas para bloqueo persistente, limpieza tras acceso correcto y respuesta HTTP 429.

## Verificación
- Pruebas locales automatizadas, sin llamar a proveedores externos.
- No se desplegó ningún cambio al servidor de producción.

## Limitaciones conocidas
- La aplicación sigue usando una contraseña compartida de instancia, no un sistema multiusuario.
- El límite está asociado a la IP que observa el servidor; en un hosting detrás de proxy, debe configurarse la infraestructura para que esta identidad sea fiable. No se confía ciegamente en `X-Forwarded-For`.
- No es una certificación de seguridad ni una versión lista para producción.
