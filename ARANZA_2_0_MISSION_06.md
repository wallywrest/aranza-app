# Aranza 2.0 — Misión 06: personalidad configurable

## Resultado

La identidad de Aranza ya puede personalizarse desde la aplicación y queda almacenada por cuenta, separada del perfil personal y de la memoria. El comportamiento base actual se conserva mientras las preferencias estén en “Como ahora”.

## Qué se añadió

- Panel “Personalidad de Aranza” con descripción libre y controles de tono, humor, iniciativa conversacional y nivel de detalle.
- Endpoints autenticados GET y PUT en /assistant-personality para que la web y futuros clientes Android usen el mismo contrato.
- Módulo personalidad.py que normaliza preferencias y las incorpora al prompt como estilo, sin conceder permisos de herramientas ni cambiar las reglas centrales.
- Tabla SQLite aditiva personalidad_aranza, aislada por cuenta.
- Exportación de datos v4 con la personalidad y reinicio de esa configuración al borrar los datos personales de la cuenta.
- Opción para restablecer la personalidad al comportamiento actual.

El perfil personal y los recuerdos existentes siguen siendo datos distintos. Los colores de la interfaz y el gatito naranja se conservaron.

## Límites de esta etapa

La personalización afecta la conversación, no autoriza acciones externas. No se añadieron notificaciones, capacidades nuevas de Android ni un APK. El panel web y el contrato de API preparan esta configuración para clientes futuros.

## Validación

- Pruebas de regresión añadidas para aislamiento por cuenta, integración con el prompt, validación de campos, exportación y borrado de datos.
- Sintaxis de Python y JavaScript: aprobada localmente.
- CI de Python 3.11 en Windows y Ubuntu: pendiente de esta publicación.
