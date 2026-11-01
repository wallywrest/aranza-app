# Aranza v1.73

## Conversaciones: metadatos persistentes

- Se agrega la tabla `conversaciones`, con clave compuesta por cuenta y conversación.
- Cada conversación recibe un título inicial derivado del primer mensaje del usuario; no se envía a un proveedor externo para titularla.
- La lista de conversaciones ahora devuelve `title` y `pinned`, ordenando primero las fijadas.
- Se agrega `PATCH /conversations/{conversation_id}` para actualizar `title` y/o `pinned` dentro de la cuenta autenticada.
- La creación/actualización de metadatos acompaña al guardado de mensajes; el borrado elimina también los metadatos.
- Las conversaciones previas se incorporan de forma aditiva al listarlas, sin modificar su contenido.
- Los metadatos se aíslan por `account_id`, incluso si dos cuentas usan el mismo `conversation_id`.

## Compatibilidad y límites

- No se modifican los endpoints existentes de chat, lectura ni borrado.
- El frontend todavía debe incorporar los controles visuales para renombrar y fijar chats; esta versión habilita y prueba el soporte persistente del backend.
- No incluye despliegue en Render ni cambios nativos de Android.

## Validación

- `pytest -q`: 228 pruebas aprobadas.
- `py_compile`: correcto para los módulos principales.
