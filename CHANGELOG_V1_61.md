# Aranza v1.61

## Validación de sesiones más estricta
- La sesión solo se acepta si la cuenta y la fecha de vencimiento firmadas coinciden exactamente con el registro persistente.
- Rechaza sesiones con campos inválidos, identificadores de cuenta vacíos o vencimientos booleanos.
- Añade pruebas de regresión para inconsistencias entre token y base de datos.

## Plantilla de despliegue
- `render.yaml` ya no fija el usuario de producción en `owner`; exige que se configure explícitamente desde el panel del proveedor.
- Añade una prueba para evitar que la plantilla vuelva a introducir el valor predeterminado.

## Límites
- Las pruebas son locales. No validan credenciales, persistencia ni disponibilidad de un despliegue real en Render.
