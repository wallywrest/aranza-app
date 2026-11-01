# Aranza v1.86

## Diagnóstico seguro de modelos y rutas por tarea

- Añade `GET /models/status`, protegido por autenticación.
- Expone únicamente nombres de proveedor/modelo, cantidad de proveedores, rutas por tarea y disponibilidad de visión.
- No expone claves API, URLs base, cabeceras ni configuración sensible.
- Añade `resumen_configuracion_modelos()` para reutilizar el diagnóstico sin acoplarlo a FastAPI.
- Añade pruebas para configuración vacía y para verificar que secretos/URLs no aparecen en el resumen.

## Validación

- `pytest -q`: 254 pruebas aprobadas.
- Compilación Python: validada.

## Límites

El endpoint informa configuración, no disponibilidad real del proveedor. No realiza llamadas de prueba ni genera costos. Las rutas especializadas siguen siendo heurísticas y solo se activan si se configuran sus variables de entorno.
