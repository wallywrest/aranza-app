# Aranza v1.7

## Aislamiento de datos: primera fase
- Añadida la columna `account_id` a mensajes y memorias, con valor `owner` para filas existentes.
- La inicialización aplica una migración aditiva si una base antigua no tiene esas columnas; conserva contenido y asigna los datos existentes al perfil legado `owner`.
- Los tokens incluyen el identificador de cuenta y la dependencia de autenticación devuelve el ámbito validado.
- Las consultas de historial, memorias, exportación y listado/eliminación de conversaciones filtran por cuenta.
- Se añadieron índices por cuenta para consultas frecuentes.
- Se incrementó la versión de la API a 1.7.0.

## Verificación
- Pruebas automatizadas de separación de datos, rechazo de acceso cruzado a conversaciones y migración de esquema legado.
- No se desplegó nada en producción.

## Límite importante
Esta versión prepara el aislamiento en la capa de datos, pero todavía solo emite sesiones para el perfil `owner` mediante la contraseña compartida de instancia. No incluye alta de usuarios, contraseñas individuales ni gestión de cuentas. No debe considerarse un sistema multiusuario completo ni listo para producción.
