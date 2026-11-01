# Aranza v1.13

## Coordinador inicial de tareas
- Añadido `coordinador.py` con clasificación heurística transparente: conversación, matemáticas, programación, análisis y escritura.
- El endpoint `/chat` selecciona la cadena de proveedores correspondiente a la tarea.
- Añadida configuración opcional de proveedor especializado para análisis, programación, matemáticas y escritura.
- El proveedor especializado se intenta primero; después se conserva la cadena general como respaldo.
- La respuesta del chat incluye el campo `task` para indicar qué ruta heurística se eligió.

## Variables opcionales
Para cada categoría `ANALYSIS`, `CODING`, `MATH` y `WRITING` se admiten:
- `ARANZA_<CATEGORÍA>_PROVIDER`
- `ARANZA_<CATEGORÍA>_BASE_URL`
- `ARANZA_<CATEGORÍA>_API_KEY`
- `ARANZA_<CATEGORÍA>_MODEL`

Si falta cualquier campo esencial, no se activa el proveedor especializado y se usa la configuración general. No es necesario configurar nada nuevo para mantener el comportamiento anterior.

## Límites conocidos
- Clasificación por reglas, no por un modelo clasificador.
- No es un sistema multiagente ni ejecuta herramientas externas.
- Las llamadas a proveedores se prueban de forma simulada.
