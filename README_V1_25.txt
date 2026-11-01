PROYECTO ARANZA v1.25

Esta versión agrega una vista previa del contexto de memoria.

Endpoint: POST /memory/preview
Autenticación: requiere la misma sesión autenticada que el resto de la API.
Ejemplo de cuerpo JSON:
{
  "query": "Ayúdame con mi proyecto de Excel",
  "limit": 8
}

La respuesta muestra los recuerdos seleccionados, sus categorías, cantidad total
almacenada y cantidad seleccionada. Solo consulta recuerdos de la cuenta autenticada
y no modifica los datos. La recuperación sigue siendo léxica, no semántica.

La vista previa está disponible como endpoint de API; todavía no tiene un control
visual propio en index.html. Esta entrega es un paquete de desarrollo, no un despliegue.
Antes de reemplazar archivos, conserva una copia de seguridad de la instalación actual.
