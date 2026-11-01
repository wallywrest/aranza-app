# Aranza v1.21

## Validación adicional de fuentes en la interfaz
- Añade una segunda validación en el navegador para resultados de búsqueda: solo acepta HTTP/HTTPS, rechaza credenciales en URL y bloquea nombres locales/reservados comunes y literales IP.
- Normaliza URLs quitando parámetros de seguimiento habituales y fragmentos, y elimina fuentes duplicadas antes de leerlas o enviarlas al modelo.
- Comprueba que la URL devuelta por el lector corresponde al mismo origen y ruta de la fuente solicitada. Si no coincide, no usa el texto leído y marca la fuente como no leída.
- Mantiene el contenido externo etiquetado como no confiable y exige que el modelo use referencias numeradas sin inventarlas.

## Validación
- Añade pruebas estáticas para el filtro de fuentes, la deduplicación y la comprobación de identidad entre URL solicitada y leída.
- Las pruebas no sustituyen pruebas de integración con red real ni una auditoría de seguridad del despliegue.
