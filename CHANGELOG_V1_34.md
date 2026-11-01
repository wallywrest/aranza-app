# Proyecto Aranza v1.34

## Memoria activa y archivada

- Se añadió el estado `active` / `archived` a los recuerdos, con migración aditiva para bases de datos existentes.
- Los recuerdos archivados siguen visibles y conservados, pero se excluyen de la selección automática de contexto.
- La interfaz muestra el estado y permite archivar o reactivar un recuerdo sin eliminarlo.
- Se añadió una ruta autenticada para cambiar el estado, con validación y aislamiento por cuenta.
- Se añadieron pruebas para selección de contexto, reactivación, autenticación y aislamiento entre cuentas.

## Validación local

- `python -m py_compile main.py`: correcto.
- `python -m pytest -q`: 91 pruebas aprobadas.
- La sintaxis JavaScript se valida por separado con `node --check`.

No se ha desplegado la aplicación ni se ha realizado una prueba integral en navegador con un proveedor de IA externo.
