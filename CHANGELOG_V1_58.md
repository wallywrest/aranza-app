# Proyecto Aranza v1.58

## Seguridad de restauración y pruebas de recuperación
- La restauración prepara la base recuperada en un archivo temporal dentro del mismo directorio.
- La copia temporal debe superar `PRAGMA integrity_check` antes de sustituir el destino.
- El reemplazo del destino usa `os.replace` para reducir el riesgo de dejar una base parcialmente escrita.
- Se limpia el archivo temporal cuando falla la restauración.
- Se añadieron pruebas para respaldo independiente, restauración, copia de seguridad previa, fuente corrupta, rutas iguales, base inexistente y limpieza temporal.

## Límites
- La restauración sigue requiriendo detener el servicio para evitar escrituras simultáneas.
- No se ejecutó un despliegue real en Render ni se probó una recuperación desde un disco remoto.
