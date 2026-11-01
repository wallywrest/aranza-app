# Proyecto Aranza v1.39

## Registro persistente de decisiones de revisión de memoria

- Añade la tabla `decisiones_revision_memoria`, creada mediante migración aditiva al inicializar la base de datos.
- Registra decisiones explícitas de revisión: `temporal`, `no_contradiccion` y `archivado`.
- Añade `POST /memory/review-decision` con autenticación, validación de decisión y comprobación de pertenencia del recuerdo a la cuenta.
- Añade `GET /memory/review-decisions`, que muestra las últimas 100 decisiones de la cuenta autenticada.
- Integra las acciones de revisión de contradicciones en la interfaz y permite consultar el historial desde el panel de memoria.
- El historial de decisiones no determina qué recuerdo es verdadero y no modifica recuerdos por sí mismo.

## Validación local

- `python -m py_compile main.py`
- `python -m pytest -q`: 102 pruebas aprobadas.
- La sintaxis de JavaScript se valida por separado con Node.js.
- Archivo ZIP comprobado con `zipfile.testzip()`.

## Limitaciones

Las coincidencias y contradicciones siguen siendo heurísticas léxicas. No se ha desplegado la aplicación ni se ha probado de extremo a extremo con un proveedor real de IA.
