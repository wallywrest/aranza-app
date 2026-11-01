# Aranza v1.33

## Historial de versiones de memoria
- Cada edición que cambia contenido o categoría guarda la versión anterior.
- Nuevo endpoint autenticado `GET /memory/{id}/history`, limitado a las 20 versiones más recientes.
- Nuevo endpoint autenticado `POST /memory/{id}/restore/{history_id}` para restaurar una versión.
- La restauración también conserva la versión actual antes de reemplazarla, para que se pueda deshacer manualmente desde el historial.
- Historial y restauración verifican la cuenta propietaria del recuerdo y de la versión.
- La interfaz incorpora el botón **Historial** para consultar y restaurar versiones.

## Validación
- `python -m py_compile main.py`: correcto.
- `python -m pytest -q`: 88 pruebas aprobadas.
- `node --check` sobre el JavaScript extraído de `index.html`: correcto.

## Límites
No se ha desplegado la aplicación ni se ha realizado una prueba completa en navegador con un proveedor de IA real.
