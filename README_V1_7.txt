ARANZA V1.7 - PARCHE DE DESARROLLO

Cambio principal:
Primera fase de aislamiento de datos por cuenta. Conversaciones y memorias incluyen account_id; los datos existentes se migran de forma aditiva al perfil legado "owner". Las rutas protegidas filtran los datos por el ámbito de la sesión.

Pruebas:
- Aislamiento de historial y memorias por cuenta.
- Una sesión no puede leer ni eliminar una conversación de otro ámbito.
- Migración desde un esquema antiguo preservando mensajes y recuerdos.

Ejecutar en el proyecto: python -m pytest -q

Límite: sigue habiendo una sola cuenta "owner" y una contraseña compartida. Esta versión no implementa alta de cuentas ni contraseñas individuales. Es un parche de desarrollo, no una versión desplegada ni lista para producción.
