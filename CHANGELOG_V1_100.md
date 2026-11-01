# Aranza v1.100 — Auditoría estática para desarrollo asistido

- Nuevo `auditoria_desarrollo.py`: inspección estática de archivos Python mediante AST y compilación en memoria.
- Detecta errores de sintaxis, rutas FastAPI potencialmente duplicadas y marcadores TODO/FIXME/XXX.
- Genera informes JSON y Markdown para que Aranza pueda resumirlos o el desarrollador revisarlos.
- Es de solo lectura: no importa módulos del proyecto, no ejecuta pruebas, no ejecuta shell, no instala dependencias ni transmite código.
- Excluye entornos virtuales, cachés, node_modules y carpetas de build.
- Incluye límites explícitos: no demuestra corrección funcional ni seguridad completa; los hallazgos necesitan revisión humana.
