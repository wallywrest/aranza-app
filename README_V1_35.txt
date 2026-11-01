PROYECTO ARANZA v1.35

Cambio principal:
Reduce recuerdos redundantes antes de incorporarlos al contexto del modelo. Mantiene el recuerdo con mejor posición en la selección y excluye duplicados exactos o con similitud léxica muy alta.

Validación local realizada:
- python -m py_compile main.py
- python -m pytest -q

Nota: la deduplicación es léxica, no comprensión semántica. No se ha desplegado la aplicación ni se ha validado una sesión completa en navegador con un proveedor de IA real.

Instalación: integrar este parche en la copia de trabajo del proyecto siguiendo el flujo de actualización existente. Haz una copia de seguridad de la base de datos antes de actualizar.
