# Aranza v1.23

## Memoria contextual

- Añade selección léxica de recuerdos relevantes según el mensaje actual.
- Limita el contexto personal enviado al modelo a ocho recuerdos en el chat y cinco durante análisis de archivos.
- Si no hay coincidencias claras, usa un pequeño conjunto de preferencias/proyectos en vez de enviar toda la memoria.
- Mantiene el ámbito por cuenta: solo recupera recuerdos del account_id autenticado.
- No usa embeddings ni hace llamadas externas adicionales para clasificar recuerdos.

## Pruebas y validación

- 68 pruebas automatizadas aprobadas localmente.
- `main.py` pasa `py_compile`.

## Limitaciones

- La relevancia es léxica, no semántica; puede omitir recuerdos formulados con sinónimos.
- No se ha validado contra proveedores reales ni desplegado en el servidor.
- Se recomienda conservar la versión anterior y respaldar SQLite antes de instalar.
