# Proyecto Aranza v1.2 - parche aislado

## Cambios incluidos
- Se conserva el backend y la interfaz existentes como base.
- Se añade una tabla SQLite `sesiones` para registrar tokens activos y sus vencimientos.
- La validación de tokens comprueba que la sesión siga activa en la base de datos.
- Se añade `POST /logout` para revocar una sesión en el servidor.
- El botón «Cerrar sesión» intenta revocar la sesión remota y después limpia el token local.
- Se añaden pruebas de regresión para login correcto, logout con revocación, token inválido y contraseña incorrecta.

## Verificación realizada
- `python -m py_compile main.py`: correcto.
- `python -m pytest -q`: 4 pruebas aprobadas.
- Las pruebas sustituyen el cliente Groq por un stub; no hacen llamadas a un proveedor externo.

## Límites conocidos
- Este parche sigue usando una contraseña compartida configurada por variable de entorno; no implementa cuentas múltiples ni hash de contraseña almacenada.
- El limitador de intentos continúa en memoria.
- La autorización por recurso y el aislamiento de conversaciones/memorias entre varias cuentas no se resuelven aquí. La versión actual está planteada como instancia personal de una sola cuenta.
- No se han probado despliegue, dominio, CORS real, disco persistente ni dispositivos Android.
- La voz, la coordinación multi-modelo y la automejora no se implementan en este parche.

## Aplicación
Esta carpeta es una copia de trabajo aislada. No sustituye los archivos publicados. Antes de desplegar, compara los cambios, respalda la base de datos real y ejecuta las pruebas en el entorno de destino.
