Proyecto Aranza v1.41

Esta versión mejora el contexto histórico de las revisiones de memoria. Al comprobar un recuerdo, Aranza busca entre las decisiones previas de ese mismo recuerdo la que más se parece al texto propuesto. Así una decisión reciente sobre un texto distinto no tapa una revisión antigua que sí corresponde.

Seguridad: las revisiones se consultan dentro de la cuenta autenticada. No se aplican cambios automáticos a los recuerdos.

Limitación: la coincidencia es léxica y no demuestra equivalencia semántica.

Validación local recomendada:
  python -m py_compile main.py
  python -m pytest -q

No desplegado. Es un parche de desarrollo.
