PROYECTO ARANZA v1.13 - COORDINADOR INICIAL DE TAREAS

NOVEDADES
- Aranza clasifica solicitudes en conversación, matemáticas, programación, análisis o escritura mediante reglas transparentes.
- Puede intentar un proveedor especializado para matemáticas, programación, análisis o escritura.
- Si el proveedor especializado falla, el enrutador conserva los proveedores generales como respaldo.
- /chat devuelve el campo "task" con la ruta elegida.
- No se requiere configuración nueva: sin proveedores especializados se usa la configuración general existente.

CONFIGURACIÓN OPCIONAL
Para cada categoría ANALYSIS, CODING, MATH y WRITING se pueden definir ARANZA_<CATEGORÍA>_PROVIDER, ARANZA_<CATEGORÍA>_BASE_URL, ARANZA_<CATEGORÍA>_API_KEY y ARANZA_<CATEGORÍA>_MODEL. Deben configurarse los tres campos esenciales BASE_URL, API_KEY y MODEL para activar esa ruta.

VALIDACIÓN
Las pruebas automatizadas cubren clasificación y selección de proveedor. Las llamadas externas son simuladas; no se ha desplegado la versión ni probado con claves reales.

LÍMITES
La clasificación es heurística y puede equivocarse. Esto no es todavía coordinación multiagente ni ejecución de herramientas. No pegues claves API en index.html ni en repositorios.
