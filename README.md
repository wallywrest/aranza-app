
### Protección contra pérdida de la base persistente

En despliegues con disco persistente, configura `ARANZA_REQUIRE_PERSISTENT_STORAGE=true`. La plantilla `render.yaml` ya lo activa. Tras inicializar la base, Aranza crea un marcador junto al archivo SQLite; si en un reinicio posterior falta la base pero el marcador sigue presente, el servicio se detiene para evitar crear una instalación vacía por accidente. Revisa el montaje del disco y restaura un respaldo antes de reiniciar. Esta protección no reemplaza los respaldos.

### Diagnóstico local de almacenamiento (v1.65)

Para revisar una base sin crearla ni modificarla, ejecuta:

```bash
python backup_db.py doctor --source /ruta/a/aranza.sqlite3
```

El comando informa si falta el archivo, si pasa `PRAGMA integrity_check`, si existen archivos WAL/SHM y si el directorio padre parece escribible. Devuelve código distinto de cero si la base falta, está dañada o el directorio no es escribible. Ejecuta el diagnóstico con el servicio detenido para evitar resultados confusos por escrituras concurrentes.

La restauración debe seguir ejecutándose con el servicio detenido:

```bash
python backup_db.py restore --source /ruta/al/respaldo.sqlite3 --confirm
```

La restauración crea un respaldo preventivo de la base actual y valida la copia antes de reemplazarla. Esto reduce riesgos, pero no sustituye una copia externa ni una prueba de restauración en el entorno real.

### Auditoría de respaldos (v1.66)

Para comprobar la integridad y antigüedad de las copias sin modificarlas ni eliminarlas:

```bash
python backup_db.py audit-backups --directory ./backups --max-age-days 7
```

El comando revisa archivos `.sqlite3`, `.sqlite` y `.db`, informa cuáles pasan `PRAGMA integrity_check`, calcula su antigüedad y señala si existe al menos una copia válida dentro del plazo indicado. Devuelve código distinto de cero si falta el directorio, no existe un respaldo válido reciente o se detectan copias inválidas. No borra copias corruptas: deben revisarse manualmente. Ejecuta la auditoría con el servicio detenido para obtener un inventario consistente.

### Manifiesto y trazabilidad de respaldos (v1.67)

Cada respaldo nuevo genera un archivo lateral `<respaldo>.json` con versión del formato, nombre del archivo, origen, fecha UTC, tamaño, SHA-256, resultado de integridad y cantidad de tablas. El manifiesto se escribe mediante archivo temporal y reemplazo atómico. La auditoría valida tamaño y huella para detectar cambios posteriores; los respaldos antiguos sin manifiesto siguen siendo compatibles y se cuentan por separado. Un manifiesto ilegible, incompatible o con huella distinta hace fallar la auditoría. La huella ayuda a detectar alteraciones accidentales, pero no es una firma criptográfica contra alguien que pueda modificar tanto el respaldo como su manifiesto.

### Historial de auditorías (v1.68)

Puedes guardar un registro acumulativo de cada auditoría, incluidas las que fallan, con:

```bash
python backup_db.py audit-backups --directory ./backups --max-age-days 7 --history-file ./backups/audit_history.jsonl
```

El historial JSONL añade una línea por ejecución con fecha UTC, conteos, estado y error resumido. No almacena el contenido de la base. La opción es explícita: sin `--history-file`, la auditoría no escribe un historial. Para automatizarlo, programa este comando en el Programador de tareas de Windows o `cron` y revisa tanto el código de salida como el archivo histórico; Aranza no instala tareas programadas automáticamente.

### Política de alertas de respaldos (v1.69)

Para evaluar el historial acumulado de auditorías y obtener alertas en JSON:

```bash
python backup_db.py backup-status --history-file ./backups/audit_history.jsonl --max-consecutive-failures 2 --max-record-age-hours 24
```

El comando avisa si falta el historial, está vacío o contiene líneas inválidas, si la última auditoría es demasiado antigua, si se acumulan fallos consecutivos, si no hay un respaldo reciente válido o si la última auditoría detectó copias/manifiestos inválidos. Devuelve código distinto de cero ante alertas, lo que permite conectarlo a un monitor externo o a una tarea programada. No envía correos ni instala tareas automáticamente. El historial debe generarse con `audit-backups --history-file ...`.

### Ensayo aislado de restauración (v1.70)

Antes de depender de un respaldo, puedes comprobar que SQLite logra copiarlo y que el esquema resultante coincide, sin reemplazar la base activa:

```bash
python backup_db.py verify-restore --source ./backups/aranza_....sqlite3
```

El comando crea una base temporal, ejecuta comprobaciones de integridad y compara las definiciones de las tablas; después elimina el archivo temporal. No modifica el respaldo ni la base activa y no requiere `--confirm`. Es una prueba técnica aislada, no una garantía de que la aplicación completa funcione con ese respaldo en producción.

### Validación del manifiesto antes de restaurar (v1.71)

Los comandos `verify-restore` y `restore` verifican ahora el manifiesto JSON asociado cuando existe. Si el archivo no corresponde al respaldo o su tamaño/SHA-256 no coincide, la operación se detiene antes de sustituir la base de destino. Los respaldos antiguos sin manifiesto siguen siendo compatibles, pero no tienen checksum verificable por este mecanismo.

```bash
python backup_db.py verify-restore --source ./backups/aranza_....sqlite3
```

El informe incluye `manifest_status` y `checksum_verified`. SHA-256 detecta modificaciones accidentales o inconsistencias respecto del manifiesto; no es una firma criptográfica y no protege si ambos archivos se alteran juntos.

### Arquitectura Android y modo sin conexión (v1.72)

La ruta propuesta para Android, los permisos, el acceso rápido, el tratamiento de audio/imágenes, los límites de HyperOS y el alcance offline están documentados en `ARQUITECTURA_ANDROID_OFFLINE_V1_72.md`. Esta entrega es de planificación técnica: no contiene todavía un APK ni activa funciones nativas. Se prioriza estabilizar la PWA y sus conversaciones antes de empaquetarla con Capacitor.

### v1.73: metadatos persistentes de conversaciones

La API conserva títulos y estado de fijado por cuenta en SQLite. `GET /conversations` incluye `title` y `pinned`; `PATCH /conversations/{conversation_id}` acepta `{"title":"..."}`, `{"pinned":true}` o ambos. El frontend debe mostrar los controles correspondientes. Consulta `CHANGELOG_V1_73.md`.

## v1.74
La interfaz del historial ya permite fijar/desfijar y renombrar conversaciones usando el endpoint autenticado existente. Los metadatos del servidor tienen prioridad sobre títulos locales antiguos. La opción de ocultar sigue afectando solo al navegador actual.

Consulta `CHANGELOG_V1_75.md` para el análisis visual opcional.

### v1.75: recepción y análisis visual opcional

La interfaz permite adjuntar imágenes JPG, PNG y WEBP de hasta 5 MB. El backend valida extensión, MIME declarado, firma básica y tamaño; procesa los bytes en memoria y no guarda la imagen. El análisis visual requiere configurar un proveedor compatible con entrada multimodal, de forma independiente al modelo de chat:

```env
ARANZA_VISION_PROVIDER=nombre-del-proveedor
ARANZA_VISION_BASE_URL=https://proveedor.example/v1
ARANZA_VISION_API_KEY=tu_clave
ARANZA_VISION_MODEL=modelo-con-vision
ARANZA_VISION_TIMEOUT_SECONDS=60
```

Si no se configura, Aranza informa que la función no está disponible; no intenta enviar imágenes a un modelo de texto que quizá no las admita. Las imágenes no se almacenan ni se incorporan al historial persistente. El análisis visual puede equivocarse y debe revisarse. El proveedor recibe la imagen cuando se solicita el análisis, por lo que aplican sus propias condiciones de privacidad.

### v1.76: voz desde el navegador

La interfaz incorpora dictado en español de México cuando existe `SpeechRecognition`/`webkitSpeechRecognition`, y lectura en voz alta por mensaje mediante `speechSynthesis`. No se envían grabaciones al backend ni se guardan. El soporte y las condiciones de privacidad del reconocimiento dependen del navegador; no se garantiza dictado offline. Consulta `CHANGELOG_V1_76.md`.

### PWA instalable (v1.77)

La app incluye `manifest.webmanifest`, icono SVG y un Service Worker que almacena únicamente la carcasa pública. Las API y respuestas autenticadas no se guardan en caché. En Android/Chrome, abre la app mediante HTTPS y usa el menú del navegador para instalarla cuando aparezca la opción. El modo sin conexión de esta versión solo recupera la interfaz; el chat y las funciones de servidor requieren conexión.

### v1.78: borradores locales y conectividad

El compositor conserva borradores de texto por cuenta y conversación en el almacenamiento local del navegador. Los restaura al volver a abrir el chat, pero nunca los envía automáticamente. Se muestra el estado de conexión. Los borradores no se sincronizan entre dispositivos y permanecen en el perfil del navegador hasta que se borran; evita usar esta función en dispositivos compartidos. La API y el modelo siguen requiriendo internet.

### v1.79: adjuntos múltiples

La interfaz permite seleccionar hasta cinco documentos e imágenes en un mismo mensaje. Cada archivo se valida individualmente (máximo 5 MiB) y se procesa secuencialmente usando los endpoints existentes de análisis de documentos e imágenes. Los resultados se agrupan en una sola respuesta. Los archivos no se guardan en el servidor. El análisis visual sigue dependiendo de un proveedor multimodal configurado. Los archivos se analizan por separado, no como un único contexto multimodal compartido.

### v1.80: preparación inicial para Android con Capacitor

Se añade el esqueleto de configuración de Capacitor (`capacitor.config.ts` y `package.json`) y la guía `ANDROID_CAPACITOR_V1_80.md`. La carpeta Android se genera localmente con `npm run cap:add:android`; no se distribuye dentro del ZIP. Esta versión no contiene APK ni activa permisos nativos. Antes de empaquetar, configura `window.ARANZA_API_BASE` con la URL HTTPS del backend y autoriza únicamente el origen real de Capacitor en `ARANZA_ALLOWED_ORIGINS`.


## v1.81: preparación segura para Android

Ejecuta `python verificar_android.py` para validar `ARANZA_API_BASE` y `ARANZA_ALLOWED_ORIGINS` antes de preparar Capacitor. Consulta `ANDROID_SEGURIDAD_SESION_V1_81.md`. Esta comprobación no compila APK ni sustituye las pruebas en dispositivo.

## v1.82: política de permisos Android

Se incorpora `android-template/app/src/main/AndroidManifest.xml` como plantilla mínima y `ANDROID_PERMISOS_V1_82.md` con la política de cámara, micrófono, selector del sistema y seguridad de tráfico. Integra la plantilla en el manifiesto generado por Capacitor y revisa el Merged Manifest antes de compilar. No es un APK ni activa permisos en ejecución.

## v1.83: auditoría estática Android

Ejecuta `python verificar_android_release.py` para revisar configuración de Capacitor, permisos mínimos, depuración WebView, tráfico HTTP y respaldo automático. Consulta `ANDROID_AUDITORIA_RELEASE_V1_83.md`. Es una comprobación estática: no compila ni firma APK y no sustituye pruebas en dispositivo. Android Keystore y almacenamiento nativo seguro de sesiones siguen pendientes.

## v1.84 — Seguridad de sesiones Android

Consulta `SEGURIDAD_SESIONES_ANDROID_V1_84.md` para el hallazgo confirmado sobre `sessionStorage`/`localStorage`, la arquitectura propuesta y los criterios previos a integrar almacenamiento nativo seguro. Esta versión es documental y no afirma que Android Keystore esté implementado.

## v1.85: exportación completa y borrado de datos personales

`GET /export` genera el formato `aranza-export-v2`, que incluye conversaciones, metadatos (títulos y fijados), memorias, historial de cambios y decisiones de revisión. `DELETE /account/data` elimina el contenido personal de la cuenta autenticada y revoca sus sesiones, pero conserva la cuenta. Requiere la contraseña actual y la frase exacta `ELIMINAR MIS DATOS`; después será necesario iniciar sesión otra vez. La operación no sustituye las políticas de retención de snapshots o respaldos externos. Consulta `CHANGELOG_V1_85.md`.

## Diagnóstico seguro de modelos (v1.86)

Con una sesión autenticada, `GET /models/status` muestra proveedores y modelos configurados, rutas especializadas por tarea y si existe un proveedor de visión. El resumen no incluye claves API ni URLs base y no hace llamadas externas: indica configuración, no disponibilidad real.


Versión de trabajo actual: **v1.86**. Consulta `CHANGELOG_V1_86.md` para los cambios de esta entrega.

## v1.87: planificador seguro de herramientas

El coordinador añade `planificar_herramientas()` y el endpoint de chat devuelve `execution_plan` con herramientas candidatas, motivos, estado y requisito de confirmación. El planificador no ejecuta herramientas ni realiza llamadas externas. Las acciones con posibles efectos secundarios se marcan para confirmación explícita. Consulta `CHANGELOG_V1_87.md`.

Versión de trabajo actual: **v1.87**.

## v1.88: contratos y ejecución unificada de herramientas

Se añade `GET /tools/catalog` y `POST /tools/execute`, ambos autenticados. El ejecutor permite únicamente `web_search`, `web_research` y `read_webpage`, todas de solo lectura, con validación estricta de argumentos y duración reportada. El catálogo también documenta `file_analysis` y `vision`, que requieren cargas multipart y continúan en sus endpoints dedicados. No existe ejecución arbitraria de código, comandos, acciones externas ni acceso a archivos locales. Los resultados web son contenido externo no confiable. Consulta `CHANGELOG_V1_88.md`.

Versión de trabajo actual: **v1.88**.

## v1.89: ejecución acotada de búsqueda web en el chat

El chat ahora ejecuta una búsqueda web de solo lectura cuando el planificador detecta que la solicitud la necesita. La ejecución está limitada a una búsqueda y tres resultados por turno; el contenido externo se marca como no confiable antes de pasarlo al modelo. La respuesta incluye `tool_trace` con estado y duración. Si falla la búsqueda, Aranza no inventa fuentes. Las acciones con efectos externos siguen sin ejecutarse y requieren un flujo de aprobación separado. Consulta `CHANGELOG_V1_89.md`.

Versión de trabajo actual: **v1.89**.

### v1.91: evaluación prudente de fuentes

La investigación devuelve `source_assessment`, con señales observables y limitaciones por fuente. No presenta HTTPS o dominios institucionales como garantía de veracidad. La detección semántica de contradicciones no está implementada todavía.

## v1.92: comparación conservadora de afirmaciones

`source_assessment.claim_comparison` compara oraciones de páginas que sí se pudieron leer. Señala posibles discrepancias cuando encuentra términos compartidos y cifras o polaridad diferentes. Cada candidato incluye extractos, dominios, enlaces y una advertencia de revisión contextual. No decide qué fuente tiene razón ni garantiza detectar paráfrasis o contradicciones semánticas. Solo compara hasta cinco fuentes leídas y devuelve hasta ocho candidatos. Consulta `CHANGELOG_V1_92.md`.

Versión de trabajo actual: **v1.92**.

## v1.93: matriz de evidencia y señales temporales

`source_assessment.evidence_matrix` ofrece identificadores por fuente y resume nivel de evidencia, contexto y señal temporal. Las fechas ISO o escritas en español se extraen únicamente de páginas leídas y se marcan como candidatas no verificadas. La antigüedad se clasifica en intervalos para ayudar a contextualizar información cambiante, sin convertirla en una puntuación de veracidad. Consulta `CHANGELOG_V1_93.md`.

Versión de trabajo actual: **v1.93**.

## v1.94 — Biblioteca privada de investigaciones

Aranza incorpora una biblioteca persistente de expedientes de investigación en SQLite. Endpoints autenticados: `POST /research/library` para guardar, `GET /research/library` para listar (opcionalmente filtrado por `conversation_id`), `GET /research/library/{research_id}` para consultar y `DELETE /research/library/{research_id}` para eliminar. Cada expediente puede almacenar título, consulta, resumen, fuentes y evidencia. Los expedientes quedan aislados por cuenta y se incluyen en la eliminación de datos personales. El guardado es explícito; la interfaz visual y la exportación se mantienen pendientes. Consulta `CHANGELOG_V1_94.md`.

## v1.95 — Biblioteca visual de investigaciones

La biblioteca privada de v1.94 ahora cuenta con un panel integrado en `index.html`: búsqueda por título/consulta/resumen, lista de expedientes, detalle con fuentes y evidencia, eliminación explícita y exportación Markdown autenticada. El backend agrega el parámetro `q` a `GET /research/library` y `GET /research/library/{id}/export`. Todas las operaciones permanecen limitadas a la cuenta autenticada. La biblioteca sigue guardando únicamente expedientes que el usuario haya solicitado conservar; no se activa almacenamiento automático de investigaciones.

Validación de desarrollo: consulta `CHANGELOG_V1_95.md` y `test_research_library_v195.py`.

## v1.96 — Biblioteca de conocimiento conectada

La biblioteca ahora admite etiquetas, filtros por etiqueta, relaciones bidireccionales entre investigaciones y un historial de snapshots cuando cambian las etiquetas. Las relaciones e historial están aislados por cuenta; la eliminación de un expediente limpia sus dependencias y la eliminación de datos personales incluye las tablas nuevas. Las exportaciones Markdown incluyen etiquetas. El historial de esta versión cubre cambios de etiquetas, no un versionado completo de todo el contenido.

Validación local de v1.96: 300 pruebas automatizadas, compilación Python y comprobación sintáctica JavaScript superadas. No implica despliegue ni validación en producción.

### v1.97 — Búsqueda global explicable
La biblioteca incorpora búsqueda local ponderada por relevancia sobre títulos, consultas, etiquetas, resúmenes y metadatos de fuentes. Devuelve términos coincidentes y cobertura para explicar el ranking. No usa embeddings ni debe describirse como búsqueda semántica neuronal. Las consultas permanecen en el backend y el acceso se limita a la cuenta autenticada.

### v1.98: contexto de investigaciones previas

Aranza puede recuperar hasta tres expedientes relevantes de su biblioteca privada durante el chat. La recuperación usa el ranking léxico ponderado local de v1.97, aplica umbrales de coincidencia y expone una traza `research_context`. Los expedientes se etiquetan en el prompt como referencias potencialmente desactualizadas y no verificadas en el turno actual. No son embeddings semánticos ni sustituyen la investigación web reciente.

## v1.99: historial reversible de investigaciones

Los expedientes de la biblioteca ahora admiten edición completa mediante `PUT /research/library/{research_id}`. Cada edición guarda una instantánea previa. Para recuperar una versión se usa `POST /research/library/{research_id}/history/{history_id}/restore`; antes de restaurar, el estado actual también se conserva, por lo que la operación es reversible. Ambas rutas verifican la propiedad por cuenta y reutilizan el historial existente.

## v1.100 — Auditoría estática de desarrollo

Se incorpora `auditoria_desarrollo.py`, una herramienta local y de solo lectura que revisa sintaxis Python, detecta rutas FastAPI potencialmente duplicadas y localiza marcadores TODO/FIXME/XXX. Produce informes JSON y Markdown. No ejecuta el proyecto ni sus pruebas, no importa módulos del usuario y no envía código a servicios externos. Es una ayuda de revisión, no una certificación de calidad o seguridad. Ejecutar desde la carpeta del proyecto: `python auditoria_desarrollo.py .`.

## Revisión de auditorías (v1.101)

Después de generar `auditoria_aranza.json` con `auditoria_desarrollo.py`, puedes resumirlo sin modificar el proyecto:

```bash
python informe_auditoria.py auditoria_aranza.json
```

Se generan `revision_auditoria.json` y `revision_auditoria.md`. La clasificación es heurística: revisa manualmente cada hallazgo. Esta herramienta no cambia archivos ni corrige código.
