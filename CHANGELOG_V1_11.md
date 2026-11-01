# Aranza v1.11 - Memoria explícita desde el chat

## Novedades

- Aranza detecta solicitudes explícitas como "recuerda que...", "quiero que recuerdes que...", "guarda en memoria que..." y "anota que...".
- El recuerdo se guarda en la cuenta autenticada y aparece en el panel existente «Memoria de Aranza» para revisarlo o eliminarlo.
- La respuesta confirma cuando se guardó un recuerdo nuevo.
- Se evita duplicar recuerdos idénticos dentro de la misma cuenta.
- Se rechazan automáticamente solicitudes de guardar contraseñas, claves API, tokens de acceso y datos similares de autenticación.
- No se guarda automáticamente el resto de los mensajes: la intención explícita es obligatoria para esta primera versión.
- La API de chat devuelve `memory_saved` y `memory_id` para que el cliente pueda conocer el resultado.

## Validación

- `python -m py_compile main.py`
- `python -m pytest -q`: 31 pruebas aprobadas.
- Las pruebas de chat usan un modelo simulado; no realizan llamadas de pago a un proveedor externo.

## Límites

- No hay extracción automática general de cada conversación; esta versión prioriza consentimiento explícito y evita guardar todo indiscriminadamente.
- La detección usa reglas sencillas, no un modelo clasificador.
- Sigue siendo una sola cuenta configurada; no se ha desplegado en producción.
