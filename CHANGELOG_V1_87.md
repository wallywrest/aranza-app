# Aranza v1.87 — Planificador seguro de herramientas

- El coordinador genera un plan estructurado para búsqueda web, análisis documental, visión y recuperación de memoria cuando el texto sugiere esas capacidades.
- Las acciones potencialmente externas o irreversibles se marcan con `requires_confirmation: true`.
- Cada herramienta aparece como `planned_not_executed`: el plan no ejecuta herramientas ni afirma que se hayan ejecutado.
- La respuesta de chat incorpora el campo aditivo `execution_plan`; se conservan los campos y endpoints existentes.
- El planificador es determinista y no hace llamadas de red ni genera costos.

Limitación: es planificación heurística, no un agente autónomo ni un sistema de permisos completo. La ejecución real sigue dependiendo de los flujos existentes y debe implementarse con autorización y validación por herramienta.
