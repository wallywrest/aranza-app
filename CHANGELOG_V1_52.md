# Proyecto Aranza v1.52

## Verificación de definiciones de casos en benchmarks

- Los casos de informes pueden incluir `fingerprint`, una huella textual de la definición del escenario evaluado.
- El comparador identifica casos coincidentes cuyo `fingerprint` cambió entre baseline y candidato.
- El informe JSON incluye `changed_definitions`, `missing_fingerprints`, `case_definitions_match`, y contadores asociados.
- Nuevo argumento `--require-case-fingerprints`: exige huellas en los casos emparejados y falla con código 1 si faltan o difieren.
- Los informes antiguos siguen siendo válidos en modo normal; las huellas son opcionales salvo que se active el modo estricto.
- Una huella debe generarse de forma estable a partir de la definición del caso (por ejemplo, consulta, recuerdos de referencia y configuración). Una etiqueta manual no garantiza que el contenido sea idéntico.

## Motivo

Comparar dos métricas bajo el mismo nombre de caso no garantiza que se haya evaluado el mismo escenario. Esta versión ayuda a detectar cambios de definición que podrían invalidar una comparación.

## Límites

El comparador no genera huellas automáticamente ni verifica que la huella represente correctamente la definición. Esa responsabilidad corresponde al generador de benchmarks.
