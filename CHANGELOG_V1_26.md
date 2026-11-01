# Aranza v1.26

## Vista previa de memoria integrada en la interfaz
- Se añadió una sección «Probar qué recuerda Aranza» al panel de memoria.
- Permite enviar una consulta al endpoint autenticado `POST /memory/preview` desde la interfaz.
- Muestra el número de recuerdos seleccionados frente al total y presenta cada recuerdo con su categoría.
- Estados visuales para carga, resultado vacío y error.
- La vista previa es de solo lectura; no cambia los recuerdos guardados.
- El renderizado del contenido de recuerdos usa `textContent`/nodos de texto para evitar interpretar contenido guardado como HTML.

## Validación
- Pruebas de Python y comprobación de sintaxis ejecutadas al empaquetar.
- Se comprobó la sintaxis JavaScript si Node.js está disponible.
- El paquete excluye bases de datos locales, cachés y bytecode.

## Límites
- No desplegado ni probado con proveedor de IA real.
