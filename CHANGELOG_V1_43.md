# Proyecto Aranza v1.43

## Línea temporal de recuerdos
- Añade `GET /memory/timeline` para consultar en una sola respuesta los recuerdos actuales y las versiones anteriores guardadas al editar o restaurar.
- La consulta está aislada por cuenta autenticada.
- El parámetro `limit` se limita de forma segura al rango 1–200.
- Los eventos se ordenan por fecha registrada y después por identificador.
- La respuesta explica los límites: no es un registro de todas las conversaciones ni prueba cuándo cambió una preferencia real.
- No se modifica ni elimina ningún recuerdo; endpoint de solo lectura.

## Validación
- Pruebas para versiones actuales/anteriores, aislamiento entre cuentas y límite máximo.
