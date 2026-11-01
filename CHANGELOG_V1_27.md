# Aranza v1.27

## Administración de memoria desde la interfaz
- Al guardar un recuerdo se puede elegir una categoría: general, preference, project, goal o personal.
- La lista de recuerdos muestra su categoría y permite filtrar por ella.
- Se añadió una acción para borrar todos los recuerdos de la cuenta autenticada, con confirmación explícita.
- La lista se representa mediante nodos DOM y `textContent`, evitando interpretar el contenido de los recuerdos como HTML.

## Seguridad y límites
- Se reutilizan los endpoints autenticados existentes (`POST /memory` y `DELETE /memory`).
- El borrado total es irreversible; la interfaz lo advierte antes de enviar la petición.
- No se añadió una nueva dependencia ni servicio externo.
