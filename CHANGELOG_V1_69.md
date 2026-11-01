# Proyecto Aranza v1.69

## Alertas de política de respaldos

- Se añade `backup-status` para evaluar el historial JSONL de auditorías sin modificarlo.
- Detecta historial inexistente, ilegible o vacío, registros malformados, auditorías demasiado antiguas, fallos consecutivos, ausencia de respaldo reciente válido y copias/manifiestos inválidos registrados en la última auditoría.
- Configura el umbral de fallos consecutivos y la antigüedad máxima del último registro mediante opciones CLI.
- El comando devuelve código 1 cuando hay alertas, para permitir que Programador de tareas, cron o un monitor externo detecten el fallo.
- Incluye pruebas para historial ausente, fallos consecutivos, auditorías antiguas y líneas malformadas.

La herramienta no instala tareas programadas ni envía notificaciones externas por sí sola. Las alertas se muestran como JSON en consola y mediante el código de salida.
