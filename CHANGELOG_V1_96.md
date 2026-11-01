# Aranza v1.96 — Biblioteca de conocimiento conectada

## Implementado
- Etiquetas por expediente: hasta 20, normalizadas, sin duplicados y con límite de 40 caracteres.
- Filtro de biblioteca por etiqueta, además de la búsqueda existente por título, consulta y resumen.
- Relaciones bidireccionales entre investigaciones de la misma cuenta.
- Vista de investigaciones relacionadas dentro del detalle del expediente.
- Historial de revisiones al modificar etiquetas, con snapshots acotados y consulta autenticada.
- Exportación Markdown incluye las etiquetas.
- Al eliminar un expediente se limpian sus relaciones e historial.
- La eliminación de datos personales incluye las nuevas tablas.
- Migración aditiva para bases existentes: agrega `tags_json` sin borrar expedientes.

## Seguridad y límites
- Todas las operaciones usan `account_id` del principal autenticado.
- No se permite relacionar expedientes de cuentas distintas ni una investigación consigo misma.
- No se ejecutan acciones externas ni se comparte información entre cuentas.
- El historial registra cambios de etiquetas en esta versión; no es todavía un versionado completo del contenido de fuentes y resumen.

## Validación
- 300 pruebas automatizadas superadas.
- Compilación Python correcta.
- JavaScript validado con `node --check`.
- No desplegada en Render ni probada con proveedor real en producción.
