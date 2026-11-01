# Proyecto Aranza v1.32

## Revisión y actualización con confirmación
- La revisión de vigencia ahora ofrece «Proponer actualización» en cada candidato detectado.
- La persona puede editar el contenido y revisar/cambiar la categoría antes de aceptar.
- La actualización solo se envía tras confirmación explícita y utiliza el endpoint autenticado `PUT /memory/{memory_id}`.
- Se validan categorías permitidas en la interfaz; cancelar, dejar vacío o conservar el mismo texto no modifica el recuerdo.
- Después de aceptar, se recarga la lista y se vuelve a ejecutar la auditoría.

## Límites
- La auditoría sigue siendo heurística: una expresión temporal no demuestra que el recuerdo esté desactualizado.
- La propuesta se construye manualmente por el usuario; no hay inferencia automática de hechos actuales.
- Sin despliegue ni validación con proveedores externos en esta versión.
