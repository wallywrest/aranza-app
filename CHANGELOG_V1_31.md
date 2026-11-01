# Aranza v1.31

- Añade una revisión heurística de recuerdos que contienen expresiones temporales o de cambio.
- Incorpora `GET /memory/audit`, protegido por autenticación y limitado a los recuerdos de la cuenta activa.
- Añade el botón «Revisar vigencia» al panel de memoria.
- La revisión es de solo lectura: no actualiza ni elimina recuerdos y advierte que las coincidencias no prueban que un recuerdo esté obsoleto.
- Añade pruebas para la detección, el límite de resultados y la autenticación.
