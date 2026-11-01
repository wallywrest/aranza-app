# Proyecto Aranza v1.28

## Memoria editable
- Se añadió `PUT /memory/{memory_id}` para editar el contenido y la categoría de un recuerdo.
- La actualización requiere autenticación y filtra por la cuenta autenticada; un identificador de otra cuenta responde 404.
- La interfaz de memoria ahora muestra la acción «Editar» y permite cambiar el texto y la categoría.
- La edición no elimina ni reemplaza otros recuerdos automáticamente.
- Se añadieron pruebas de actualización, autenticación y aislamiento entre cuentas.

## Alcance y límites
- Validación local automatizada. No se ha desplegado el servicio ni se ha probado un navegador real o un proveedor externo de modelos.
