# Aranza v1.20

## Investigación web integrada
- Al activar la búsqueda web en el chat, Aranza busca hasta cinco resultados y trata de leer las dos primeras páginas mediante el endpoint autenticado existente.
- Cada lectura de página falla de forma independiente: si una fuente no se puede leer, el chat conserva el fragmento del buscador y continúa.
- El texto de cada página se limita a 1.800 caracteres para controlar el contexto enviado al modelo.
- El prompt marca explícitamente el contenido externo como no confiable e indica que las páginas no pueden modificar las instrucciones del sistema.
- El pie de fuentes distingue entre páginas cuyo texto se leyó y resultados de los que solo se dispone de fragmento.

## Validación
- `python -m py_compile main.py modelos.py coordinador.py busqueda_web.py lector_web.py`
- `node --check` sobre el script de la interfaz.
- `python -m pytest -q`: 60 pruebas aprobadas.

## Límites conocidos
- Las páginas se leen mediante un extractor HTML simple, sin JavaScript; el contenido puede ser incompleto.
- La lectura puede añadir latencia y fallar por bloqueos del sitio, DNS, límites de red o HTML no compatible.
- Las pruebas no sustituyen una validación con proveedores y páginas reales ni una revisión de seguridad del despliegue.
- No se desplegó nada en el servidor del usuario.
