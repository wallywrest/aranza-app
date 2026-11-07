# Auditoría arquitectónica integral de Aranza 2.0

**Fecha:** 2026-11-06  
**Checkout auditado:** C:\Users\Mel\Desktop\aranza-app-dev  
**Repositorio:** https://github.com/wallywrest/aranza-app.git  
**Rama:** aranza-v1-105-development  
**HEAD auditado:** 0fcdadab50779de6ee6d048d1837c7b4bdff742a  
**Referencia de producto:** ARANZA_2_0_MASTER_SPEC.md

> Auditoría estática del código, configuración y pruebas. No certifica producción ni sustituye pruebas de navegador, dispositivo o despliegue. No se copiaron secretos ni el contenido del perfil personal codificado en el prompt.

## 1. Resumen ejecutivo

Aranza ya es una aplicación web funcional de asistente personal de perfil único: chat autenticado, persistencia SQLite, conversaciones con título y fijado, memoria léxica editable, investigación web con biblioteca, análisis opcional de imágenes/documentos, rutas de modelo compatibles con la API de OpenAI, dictado/síntesis del navegador y una PWA que conserva su carcasa pública.

La base tiene controles valiosos: PBKDF2 para contraseñas, sesiones firmadas y revocables, límite de intentos de login, aislamiento por account_id en operaciones auditadas, contenido externo marcado como no confiable, límites por archivo y consulta web, pruebas automatizadas y CI en Ubuntu/Windows con Python 3.11. La ejecución más reciente para el HEAD reportó **337 pruebas aprobadas en cada sistema** y una advertencia de deprecación de Starlette/httpx. [GitHub Actions](https://github.com/wallywrest/aranza-app/actions/runs/42080808195).

El proyecto **todavía no es la plataforma modular, multicuenta, sincronizada y multimodal descrita como destino para Aranza 2.0**. La implementación vive principalmente en un backend monolítico (main.py, unas 2.8 mil líneas) y un único frontend (index.html, unas 1.25 mil líneas con HTML, CSS y JavaScript). Conversaciones, archivos, cachés del navegador y memoria no forman todavía un flujo de datos uniforme. Android es una preparación con Capacitor y una plantilla; offline significa recuperar la interfaz, no conversar con IA.

### Riesgos prioritarios

1. **Alto — DNS rebinding en lectura web.** Se valida DNS público y después el cliente HTTP vuelve a resolver el host, sin fijar la conexión a la dirección validada (lector_web.py:65–82): riesgo potencial de SSRF.
2. **Alto — datos personales dentro del prompt versionado.** main.py:79–215 contiene un perfil/instrucciones personales en código. Este informe no reproduce su contenido. Debe trasladarse a almacenamiento controlado por cuenta y revisarse la exposición del historial Git.
3. **Alto — CORS no permite todos los métodos de API.** Autoriza GET, POST y DELETE, pero frontend/API usan PUT y PATCH (main.py:878–884 y rutas de memoria, biblioteca y conversaciones). Un frontend de otro origen —incluido Capacitor— puede fallar en preflight.
4. **Alto — “olvidar” memoria no borra su historial.** Se elimina la fila activa, no versiones ni decisiones asociadas (main.py:812–821, 2432–2458; esquema 394–414). El contenido anterior puede seguir consultable/exportable.
5. **Alto — la exportación de cuenta omite investigaciones.** /export incluye conversaciones y memoria, pero no investigaciones, relaciones ni su historial (main.py:2461–2496), aunque el borrado de cuenta sí cubre esas tablas.
6. **Medio/alto — búsqueda web duplicada y sin minimización.** La UI ejecuta investigación, agrega el rótulo “INVESTIGACIÓN WEB” y luego llama a /chat; el coordinador reconoce ese rótulo y el backend puede buscar otra vez (index.html:683–714; coordinador.py:76–96; main.py:1330–1450). Hasta 300 caracteres del mensaje se envían sin redacción.
7. **Medio — categorías de memoria desalineadas.** La UI usa preference/project/goal/personal; la clasificación y recuperación esperan preferencias/proyectos (index.html:308,310; main.py:585–588,635). Los filtros y ponderaciones no coinciden.
8. **Medio — caché local persiste tras logout y eliminar conversación solo la oculta.** Las claves locales son globales y el logout solo limpia el token (index.html:351–394, 793–802, 1149–1153). La API tiene DELETE, pero la acción visible no la usa.
9. **Medio — adjuntos no se integran al historial remoto.** Se procesan por endpoints separados; el resultado queda en estado/caché local, no junto a /chat (index.html:660–730; main.py:1552–1675).
10. **Medio — no hay validación de integración real.** La CI cubre Python/pytest, pero no JavaScript en navegador, CORS preflight real, DNS rebinding, build Android ni privacidad de caché local.

**Conclusión:** existe una base útil y probada en autenticación, alcance por cuenta, memoria revisable, biblioteca de investigación y respaldo SQLite. Antes de añadir autonomía, offline o voz avanzada, cerrar privacidad/SSRF y definir una fuente de verdad para conversaciones, adjuntos y exportaciones.

## 2. Alcance y clasificación

Se verificaron ruta, remoto, rama, HEAD y estado antes de auditar y antes de crear este informe. El checkout correcto estaba limpio, en aranza-v1-105-development y siguiendo origin/aranza-v1-105-development. El checkout separado aranza_v1_95_work permaneció en main, limpio y en su SHA original. No se inspeccionaron valores de .env ni secretos del entorno.

Se revisaron código, esquema SQLite, frontend, módulos Python, manifiesto PWA, plantilla Android, render.yaml, dependencias, especificación maestra, pruebas y workflow. No se ejecutó la suite local: el entorno no permitió iniciar python.exe. La evidencia de ejecución es CI ya completado para el HEAD; se indican las validaciones que requieren navegador, Android o infraestructura. Ubicaciones aproximadas; pueden variar al cambiar el código.

Categorías obligatorias:
1. **IMPLEMENTADA Y VERIFICADA:** hay código y pruebas relevantes en la suite que pasó en CI; no implica cobertura completa ni prueba de producción.
2. **IMPLEMENTADA PARCIALMENTE:** existe funcionalidad útil con alcance/integración incompletos.
3. **EXISTE, PERO NECESITA VALIDACIÓN:** hay código/configuración/pruebas estáticas, falta probar comportamiento en el destino real.
4. **NO IMPLEMENTADA:** no se encontró implementación funcional.
5. **PROBLEMÁTICA O INSEGURA:** defecto concreto o contradicción de privacidad/seguridad.

## 3. Estado y arquitectura actual

    Usuario navegador
      ├─ index.html: HTML/CSS/JS
      │    ├─ localStorage / sessionStorage
      │    ├─ sw.js + manifest: caché de carcasa pública
      │    └─ Capacitor / plantilla Android (scaffold)
      └─ FastAPI main.py
           ├─ SQLite: cuentas, sesiones, mensajes, memoria, investigaciones
           ├─ coordinador.py → modelos.py → proveedor externo de texto
           ├─ herramientas.py: catálogo/validación acotados
           ├─ busqueda_web.py → DuckDuckGo
           ├─ lector_web.py → páginas públicas
           ├─ evaluacion_fuentes.py / comparador_afirmaciones.py
           ├─ conocimiento.py: ranking léxico de investigación
           ├─ extracción de documentos/PDF en memoria
           └─ proveedor opcional de visión

| Módulo/recurso | Responsabilidad |
|---|---|
| main.py | Configuración, prompt, esquema/migraciones SQLite, autenticación, endpoints, memoria, conversación, investigación y archivos. Punto central de acoplamiento. |
| modelos.py | Proveedores compatibles con chat completions, fallback, rutas por tarea y visión opcional. |
| coordinador.py | Clasificación heurística y planificación determinista; planear no equivale a actuar. |
| herramientas.py | Catálogo y validación de argumentos; conjunto pequeño, mayormente de lectura. |
| busqueda_web.py, lector_web.py | Búsqueda DuckDuckGo, normalización de enlaces y lectura de páginas públicas. |
| evaluacion_fuentes.py, comparador_afirmaciones.py | Señales heurísticas sobre fuentes/fechas/contradicciones; no verifican verdad. |
| conocimiento.py | Recuperación léxica ponderada de investigaciones. |
| backup_db.py | Diagnóstico, copia, auditoría y verificación/restauración aislada de SQLite. |
| preparar_despliegue.py, verificar_android.py, verificar_android_release.py | Preflight estático; no despliegan ni compilan Android. |
| auditoria_desarrollo.py, informe_auditoria.py, ejecutar_benchmark_memoria.py, comparar_benchmarks_memoria.py | Auditoría y benchmarks auxiliares. |
| index.html | UI monolítica: navegación, chat, memoria, historial, investigación, voz, adjuntos, persistencia local. |
| sw.js, manifest.webmanifest | Instalación PWA y caché pública de la carcasa. |
| capacitor.config.ts, android-template/ | Preparación inicial; no hay app Android generada/distribuida en el checkout. |

SQLite contiene cuentas, sesiones, intentos_login, mensajes, conversaciones, memorias, memoria_historial, decisiones_revision_memoria, investigaciones, relaciones_investigacion e historial_investigacion. Las rutas examinadas filtran por account_id y hay tests de alcance. La cuenta owner se crea al inicializar si no hay cuentas y existe contraseña; no se encontró flujo de alta/provisión de varias cuentas. Por tanto, existe base para aislamiento, pero no producto multicuenta operable.

Las migraciones aditivas corren desde inicializar_db() al iniciar (main.py:301–460), sin tabla de versiones ni reversión formal. Se configura WAL, synchronous=FULL y foreign_keys=ON, pero la mayoría de relaciones no declara claves foráneas. with conectar_db() as conn administra transacción, pero no cierra explícitamente la conexión (main.py:257–266).

## 4. Auditoría de las nueve áreas

### A. Backend

FastAPI, Pydantic, sesión Bearer, middleware, SQLite y endpoints de chat, memoria, cuenta, conversaciones, herramientas, investigación, modelos y salud. Errores de proveedor suelen convertirse en HTTP controlado; lectura web registra a veces solo la clase de error.

main.py mezcla muchas responsabilidades; handlers acceden directamente a SQLite; configuración int/float se convierte al importar sin validación central de rangos; migraciones están mezcladas con el arranque; no hay request_id/idempotencia de chat. El modelo se llama antes de persistir: un reintento puede duplicar trabajo y una falla posterior a la generación puede perder la respuesta.

**Recomendación:** separar contratos HTTP, servicios de dominio y repositorios; validar configuración al inicio; versionar migraciones; agregar idempotencia y pruebas de recuperación/atomicidad.

### B. Frontend

index.html combina estructura, estilos y lógica. Estado global, acceso directo a storage, armado de solicitudes y renderizado conviven en la misma página. El renderer escapa HTML, limita enlaces a HTTP(S), añade noopener/noreferrer y usa textContent para gran parte del contenido dinámico (index.html:472–543). No se observó CSP; los bloques inline requerirían externalización o nonce/hash.

La interfaz es responsive y usa algunas etiquetas/estados ARIA, pero no se halló batería de accesibilidad de navegador, teclado, foco de paneles o lector de pantalla. prompt()/confirm() siguen presentes y son poco consistentes en móvil.

**Recomendación:** separar API client, estado, render y vistas de chat, memoria, biblioteca y autenticación. Mantener contratos existentes hasta tener pruebas de navegador y accesibilidad.

### C. Conversaciones

| Función | Estado |
|---|---|
| IDs | UUID si existe crypto.randomUUID; fallback fecha/aleatorio (index.html:356–360). |
| Historial por conversación/cuenta | Consultas con account_id + conversation_id (main.py:463–520); tests existentes. |
| Título/fijado | Metadatos persistentes y PATCH desde UI. |
| Abrir | Carga servidor; si falla, intenta caché local (index.html:780–791). |
| Archivado | No se encontró estado ni endpoint. |
| Eliminar | UI oculta localmente; no llama al DELETE (index.html:793–802; endpoint main.py:2779–2792). |
| Búsqueda | No hay búsqueda server-side de conversaciones. |
| Exportación individual | No hay endpoint dedicado; export general incluye mensajes. |
| Sincronización local | Sin sincronización offline/conflictos; al abrir online, servidor sustituye estado mostrado. |
| Adjuntos | No se incorporan al historial remoto. |
| Historial local | Hasta 200 mensajes por conversación; claves no están separadas por cuenta. |

No se observó mezcla de historiales en consultas backend. El riesgo está en la capa local: los datos se indexan por ID, no por cuenta; logout no limpia las claves. El despliegue actual es de perfil único, pero el almacenamiento no sirve aún para cuenta múltiple/dispositivo compartido.

### D. Memoria

La memoria SQLite no se extrae de cada mensaje: el guardado busca solicitudes explícitas, rechaza patrones de credenciales/datos financieros y evita duplicados exactos (main.py:743–810). El usuario puede añadir, editar, revisar, archivar/reactivar, ver historial y restaurar. Heurísticas de similitud/contradicción sugieren revisión, no alteran datos automáticamente.

La recuperación es **léxica**: normaliza acentos, usa stopwords/recorte de sufijos, puntúa coincidencias, limita resultados y elimina duplicados (main.py:521–733). No hay embeddings. El esquema no guarda procedencia, fuente, confianza, sensibilidad ni expiración. Hallazgos: borrar deja historial/decisiones; categorías UI y backend divergen; no se distingue memoria temporal de duradera. Vista previa y explicación del ranking sí permiten inspección útil.

### E. Inteligencia y proveedores

modelos.py configura principal, fallback y rutas opcionales por tarea mediante endpoint compatible con OpenAI; crea AsyncClient por llamada, aplica timeout e informa proveedor/modelo. El fallback predeterminado puede ser el mismo proveedor. La selección de tarea es heurística, no basada en coste, latencia o salud real.

Límites de token/temperatura son globales/configurados; no se encontró uso/coste persistente, presupuesto por cuenta, rate limit de generación, circuit breaker ni streaming. /models/status presenta configuración, no disponibilidad real.

Visión tiene ruta opcional separada. No se encontraron adaptadores de embeddings, transcripción, TTS remoto/realtime o modelos locales. Identidad/estilo siguen en prompt backend; cambiar proveedor requiere pruebas de regresión.

### F. Investigación y herramientas

Búsqueda fija DuckDuckGo, consulta/resultados limitados, URLs normalizadas. Lector limita URL, DNS, MIME, HTML, texto, redirects y timeout; elimina scripts y marca contenido externo no confiable. evaluacion_fuentes.py aporta señales heurísticas. Biblioteca guarda fuentes, evidencia, etiquetas, relaciones y snapshots; tiene exportación Markdown individual.

- Validación DNS y conexión HTTP no están ligadas al mismo IP: ventana de rebinding.
- Parser depende del HTML de DuckDuckGo.
- No se detectó redacción ni confirmación específica para queries sensibles.
- Planner puede buscar por expresiones generales y no mantiene registro durable de operaciones.
- UI de búsqueda y planner de /chat se solapan y pueden repetir la consulta.
- user_approved_action solo clasifica una acción; no es sistema de consentimiento/ejecución/auditoría. No hay autonomía general.

**Recomendación:** fijar DNS al socket de conexión; validar cada salto si hay redirects; minimizar consultas, hacer visible su envío y evitar búsqueda duplicada; persistir trazas sin contenido privado.

### G. Voz y multimodalidad

- Dictado usa SpeechRecognition/webkitSpeechRecognition si existe; idioma es-MX; audio no se envía al backend.
- Síntesis usa speechSynthesis, cancela utterance anterior y se detiene al salir; no es voz realtime/streaming.
- Middleware manda Permissions-Policy con microphone=() y camera=() (main.py:887–898), en conflicto con dictado y posible cámara. Debe probarse navegador/Capacitor.
- Imágenes JPG/PNG/WEBP, 5 MiB y firma básica; se envían base64 a proveedor de visión configurado, no se guardan en SQLite.
- Documentos TXT, MD, CSV, JSON, PDF con límites y extracción en memoria. PDF se procesa sincrónicamente desde ruta async; límite por archivo no es límite global de multipart/CPU.
- Resultado no se integra al historial remoto. No hay audio realtime, transcripción servidor, interrupción de generación remota ni retención multimodal completa.

### H. Android, PWA y offline

manifest habilita instalación; sw.js cachea /, manifest e icono, excluye API/autenticación. Offline devuelve shell, no IA. Borrador se conserva localmente, no se envía solo; no hay cola ni sincronización.

capacitor.config.ts, package.json y android-template/AndroidManifest.xml son preparación. No hay proyecto Android generado, APK, firma, permisos runtime, sesión Keystore ni pruebas de dispositivo. No se encontraron push notifications. PWA instalable no es app Android completa.

**Secuencia:** estabilizar datos/sesión/sincronización web; generar/probar Capacitor; integrar storage nativo, permisos y archivos; validar dispositivos, instalación, offline declarado y recuperación.

### I. Seguridad, privacidad y mantenimiento

**Controles:** PBKDF2-HMAC-SHA256 con salt (main.py:1002–1015); token firmado con nonce, expiración y revocación; limitación de login; mensajes genéricos; WAL/synchronous=FULL; CORS con lista de orígenes; headers nosniff, DENY, no-referrer; límites de entrada/archivos; procesamiento temporal; alcance por cuenta en rutas revisadas; guard de almacenamiento persistente; utilidades de respaldo.

**Brechas:** CORS omite PUT/PATCH; micrófono/cámara bloqueados por policy; falta CSP; HSTS depende del esquema percibido por FastAPI y proxy; token en sessionStorage es accesible a JS same-origin; mensajes/borradores quedan en localStorage tras logout; borrado/export no son completos; migraciones no versionadas; relaciones dependen de borrado manual; CI no muestra escaneo de vulnerabilidades.

render.yaml define servicio y disco persistente; preparar_despliegue.py valida contraseña, secreto, origen, DB y proveedor, pero es separado del arranque. Los archivos del repo no prueban dominio, auto-deploy, backups ni variables reales de Render. Confirmarlos operativamente antes de publicar. No se hizo despliegue.

## 5. Matriz de capacidades

| Capacidad | Categoría | Evidencia/alcance |
|---|---|---|
| Chat con proveedor texto | IMPLEMENTADA Y VERIFICADA | /chat, persistencia y routing en suite; no demuestra proveedor externo disponible. |
| Login, sesión, caducidad y revocación | IMPLEMENTADA Y VERIFICADA | PBKDF2, nonce SQLite, tests. |
| Alcance account_id en servidor | IMPLEMENTADA Y VERIFICADA | Consultas filtradas y test_account_scope.py; producto multicuenta no operable. |
| Conversaciones, título, pin | IMPLEMENTADA Y VERIFICADA | SQLite, rutas y tests de metadatos. |
| Búsqueda/archivo/borrado desde UI | PROBLEMÁTICA O INSEGURA | Sin búsqueda/archivo; acción solo oculta localmente. |
| Caché y borradores | IMPLEMENTADA PARCIALMENTE | Restaura en navegador; no sincroniza ni limpia logout. |
| Memoria explícita/edición/archivo/revisión | IMPLEMENTADA Y VERIFICADA | Suite de memoria y controles humanos. |
| Memoria semántica con procedencia/confianza/expiración | NO IMPLEMENTADA | Sin esos campos ni embeddings. |
| Olvido completo de memoria | PROBLEMÁTICA O INSEGURA | Permanecen versiones/decisiones. |
| Biblioteca investigación/historial/relaciones | IMPLEMENTADA Y VERIFICADA | CRUD e historial con tests v1.94–v1.99. |
| Exportación individual investigación | IMPLEMENTADA PARCIALMENTE | Descarga Markdown. |
| Exportación integral cuenta | PROBLEMÁTICA O INSEGURA | Omite investigaciones y relaciones/historial. |
| Búsqueda/lectura web | PROBLEMÁTICA O INSEGURA | Límites presentes; DNS rebinding y minimización pendientes. |
| Evaluación de fuentes | IMPLEMENTADA PARCIALMENTE | Heurística, no garantía factual. |
| Contratos básicos herramientas | IMPLEMENTADA PARCIALMENTE | Validación acotada; falta permisos/auditoría genérica. |
| Routing/fallback compatible | IMPLEMENTADA Y VERIFICADA | Tests; no costes/disponibilidad producción. |
| Embeddings/audio/modelo local | NO IMPLEMENTADA | No encontrados. |
| Análisis de archivos/PDF | IMPLEMENTADA PARCIALMENTE | Límites; CPU/multipart/contexto incompletos. |
| Análisis imagen externo | IMPLEMENTADA PARCIALMENTE | Validación y proveedor opcional; no persiste ni integra historia. |
| Dictado y síntesis navegador | PROBLEMÁTICA O INSEGURA | APIs existen; policy niega micrófono; no realtime. |
| PWA y shell offline | EXISTE, PERO NECESITA VALIDACIÓN | Manifest/SW, falta probar navegador real. |
| Chat IA offline | NO IMPLEMENTADA | API/modelo requieren red; sin modelo local. |
| Android distribuible | EXISTE, PERO NECESITA VALIDACIÓN | Scaffold/validadores; falta build, firma y dispositivo. |
| Backup/restauración SQLite | IMPLEMENTADA PARCIALMENTE | CLI; operación y retención externas. |
| CI Python 3.11 Ubuntu/Windows | IMPLEMENTADA Y VERIFICADA | 337/337 cada sistema para HEAD. |
| E2E navegador/dispositivo | NO IMPLEMENTADA | Workflow no ejecuta browser ni Android. |
| Identidad independiente del proveedor | IMPLEMENTADA PARCIALMENTE | Prompt común/rutas, pero perfil y estilo hardcodeados. |
| Agenda/autonomía supervisada | NO IMPLEMENTADA | Clasificar acción no equivale a ejecutar con permiso. |

## 6. Hallazgos priorizados

Prioridad alta: privacidad, seguridad o capacidad de ruta crítica. Media: integración/consistencia/estabilidad. Baja: mantenimiento o metadatos.

| ID/prioridad | Ubicación y evidencia | Consecuencia | Recomendación |
|---|---|---|---|
| SEC-01 — **Alta** | lector_web.py:65–82 valida DNS y luego httpx resuelve otra vez. | DNS podría cambiar y llegar a IP privada/reservada (SSRF). | Fijar conexión a IP validada; probar rebinding, IPv4/IPv6, puertos y link-local. |
| PRV-01 — **Alta** | main.py:79–215 contiene perfil/instrucciones personales versionados. | Riesgo de exposición a lectores/clones del repo; datos de cuenta mezclados con código. | No copiar a logs; revisar repo/historial y migrar a perfil por cuenta con controles y borrado. |
| API-01 — **Alta** | main.py:878–884 solo GET/POST/DELETE; rutas PUT/PATCH en 2056,2621,2671,2767. | Preflight CORS falla para frontend de otro origen/cliente empaquetado. | Autorizar métodos mínimos y probar preflight por origen/header/método. |
| PRV-02 — **Alta** | main.py:812–821,2432–2458; tablas históricas 394–414. | Olvidar deja versiones y decisiones con texto personal. | Borrar/scrub histórico en misma transacción o definir retención; test de ausencia. |
| PRV-03 — **Alta** | main.py:2461–2496 omite tablas investigación 416–445. | Exportación integral no contiene todo dato persistido. | Incluir expedientes/fuentes/evidencia/relaciones/historial; versionar y probar cobertura. |
| WEB-01 — **Media/alta** | index.html:683–714; coordinador.py:76–96; main.py:1330–1450. | Doble búsqueda; hasta 300 caracteres salen sin minimizar/redactar. | Pasar fuentes estructuradas, evitar disparador por marcador, mostrar envío y filtrar datos sensibles. |
| MEM-01 — **Media** | index.html:308,310; main.py:585–588,635. | Filtros y boosts divergen según categoría. | Enum canónico y mapeo/migración probados UI/backend. |
| CONV-01 — **Media** | index.html:793–802; DELETE API main.py:2779–2792. | La acción visible no elimina del servidor. | Distinguir ocultar de borrar remoto con confirmación. |
| PRV-04 — **Media** | index.html:351–385,586–599,1149–1153. | Datos locales sobreviven logout y no se separan por cuenta. | Retención visible, limpieza elegible y namespace account; prueba de cambio de usuario. |
| CONV-02 — **Media** | index.html:660–730; endpoints main.py:1552–1675. | Archivo/respuesta de análisis no aparecen en historial remoto/exportación. | Asociar metadatos/resultado consentido al conversation_id; no persistir binario por defecto. |
| VOICE-01 — **Media** | main.py:893 niega mic/cámara; index.html:1084–1121 usa dictado. | UI ofrece dictado que la policy puede bloquear. | Validar browser/Capacitor; permitir por capacidad/origen con consentimiento explícito. |
| DB-01 — **Media** | main.py:257–266; muchos contextos de conexión. | Context manager de transacción no cierra SQLite explícitamente. | Helper de cierre garantizado; probar excepciones/concurrencia/WAL. |
| DB-02 — **Media** | main.py:301–460 sin registro visible de versiones. | Migraciones ad hoc dificultan rollback y compatibilidad acumulada. | Migrador versionado, copia y fixtures de esquemas con reversión probada. |
| DATA-01 — **Media** | main.py:2540–2548,2621–2645 trunca JSON serializado. | Corte en mitad de JSON puede volver ilegible el expediente. | Limitar campos antes de serializar o rechazar; probar frontera de tamaños. |
| FILE-01 — **Media** | main.py:1552–1615; PDF sync dentro de endpoint async. | Body/memoria/CPU pueden excederse antes del límite del handler; event loop bloqueado. | Límite multipart en servidor, quotas/rate limits, parseo fuera del event loop y timeout. |
| MOD-01 — **Media** | main.py ~2.8k líneas, index.html ~1.25k. | Cambios acoplados dificultan prueba/revisión y regresiones. | Extraer módulos tras pruebas de caracterización, no dividir masivamente sin contratos. |
| SEC-02 — **Baja/media** | main.py:887–898, sin CSP; HSTS depende de request.url.scheme. | Falta defensa XSS; proxy puede afectar HSTS percibido. | CSP compatible/externalizar inline; validar forwarded headers en entorno controlado. |
| OPS-01 — **Baja** | main.py:871–875 version 1.18.0 pese a cambios posteriores del repo. | Metadato de API confuso/desactualizado. | Alinear versión con release/commit. |
| TEST-01 — **Baja/media** | CI muestra StarletteDeprecationWarning en combinación testclient/httpx. | Puede volverse incompatible tras actualización. | Resolver compatibilidad al actualizar; no ocultar warning sin causa. |

## 7. Pruebas y faltantes

Hay **62 archivos test_*.py en la raíz**. Cubren auth/sesiones, atomicidad de login, alcance por cuenta, metadatos de conversaciones, memoria (relevancia, duplicados, revisión, historial, archivo, benchmark, contexto), herramientas, búsqueda/lector, archivos, pipeline/historial de investigación, export/atomicidad, almacenamiento/backups, routing de modelos, PWA, borradores y validadores Android.

.github/workflows/aranza-quality.yml corre compileall y pytest -q en Ubuntu/Windows Python 3.11. Resultado para HEAD: 337 por sistema, una advertencia de deprecación. **No se reejecutaron tests locales** porque python.exe no pudo iniciarse en el entorno de auditoría.

Cobertura pendiente:
- DNS rebinding verificando IP realmente conectado, además de IP privada directa.
- Preflight CORS para métodos, Authorization, Content-Type y orígenes web/Capacitor.
- Olvido: ausencia de versiones tras borrar individual, todo y cuenta.
- Exportación con cada tabla poblada, JSON íntegro y sin datos ajenos.
- Búsqueda duplicada/query minimizada y visibilidad/consentimiento externo.
- Navegador real: recarga, logout, storage compartido, XSS/markdown, teclado y lector.
- Adjuntos/resultados a través de recarga, exportación y borrado.
- Timeout/cancelación/coste y proveedor caído.
- Build/instalación/permisos/Keystore/cámara/micrófono Android.
- Service worker offline real y distinción entre shell y chat.
- Terminación abrupta, migraciones antiguas y restauración aislada.
- Carga concurrente, multipart, PDF y abuso/rate limit.

CI no linta/compila JavaScript ni Android, no hace E2E y no muestra escaneo de vulnerabilidades de dependencias.
## 8. Deuda técnica y dependencias

Deuda principal:
- Backend/frontend monolíticos; reglas dentro de endpoints y DOM.
- La especificación describe módulos que aún no existen.
- Perfil/prompt mezclado con datos de producto/cuenta.
- Migraciones y retención sin contratos/versionado completos.
- Fuente de verdad ambigua entre SQLite y caché.
- Ocultar, archivar, sincronizar y borrar no son operaciones equivalentes.
- Proveedores configurados por heurísticas sin presupuesto/observabilidad de coste.
- PWA, Android y voz solo cuentan con evidencia mayormente estática.

Dependencias de desarrollo:
1. Seguridad/modelo de datos antes de multicuenta, sincronización, adjuntos persistentes y autonomía.
2. Contratos API, migraciones versionadas e integración antes de refactor amplio.
3. Identidad por cuenta y conversación estable antes de memoria avanzada y preferencias de proveedor.
4. Permisos, confirmación y auditoría antes de herramientas con efectos, agenda o iniciativa.
5. Sincronización/conflictos antes de offline multidispositivo.
6. API/estado y retención antes de Android completo.
7. Voz realtime depende de proveedor de audio, mic policy, cancelación, UX móvil y presupuesto.
8. Modelos locales dependen de hardware, storage, distribución y evaluación de calidad.

## 9. Arquitectura objetivo recomendada

Adoptar módulos de dominio con contratos estables y migrar gradualmente:

    Interfaces: Web/PWA ─ Android ─ Voz
                   │
    API y auth: límites · permisos · validación · request_id
                   │
    Servicios: Chat · Conversaciones · Memoria · Investigación · Archivos · Herramientas
                   │
    Dominio: identidad · procedencia · consentimiento · políticas · retención
                   │
    Adaptadores:
      Repositorios SQLite → migraciones versionadas
      Modelos: texto / visión / embeddings / audio / local
      Búsqueda y lector web aislados
                   │
    Operación: logs sin contenido privado · métricas · coste · backups · auditoría

Backend propuesto: api/routes, application/services, domain, repositories, providers, tools, storage/migrations, security y observability. Frontend: api-client, state, views/chat, views/conversations, views/memory, views/research, components, storage y accessibility. Primero pruebas de caracterización/contratos; no migrar todo en un solo cambio.

SQLite debe ser fuente de verdad online. La caché local debe ser explícita, por cuenta/conversación, con expiración/borrado; cola offline solo después de diseñar conflictos/idempotencia. Los binarios pueden seguir sin guardarse; historial puede registrar análisis y resultado que el usuario decida conservar.

## 10. Roadmap técnico y aceptación

### Fase 0 — Baseline y seguridad de cambio
- Mantener checkout/branch verificables y CI verde; documentar esquema, contratos, nombres de variables (sin valores) y dependencias de despliegue.
- **Aceptación:** CI soportada pasa; inventario reproducible; ninguna prueba usa datos de producción.

### Fase 1 — Privacidad y seguridad
- DNS rebinding, CORS, perfil codificado, consulta externa minimizada, borrado/export, retención local, micrófono, CSP/proxy.
- **Aceptación:** pruebas SSRF/preflight; exportación/borrado cubre tablas; ningún dato olvidado en historia; query sensible no sale automáticamente; revisión de PII/secretos del código e historial.

### Fase 2 — Contratos, migraciones y pruebas
- Migraciones versionadas, contratos API y pruebas E2E/browser y seguridad del pipeline.
- **Aceptación:** upgrade desde fixtures, rollback/restauración; CI backend+JavaScript+navegador; escaneo de dependencias con política explícita.

### Fase 3 — Modularización sin cambio funcional
- Extraer servicios/repositorios de main.py; separar API client, estado y vistas de index.html.
- **Aceptación:** pruebas de caracterización antes/después; contratos estables; módulos probables testeables aislados; diff atribuible.

### Fase 4 — Conversaciones completas
- Búsqueda, archivo, borrado remoto distinto de ocultar, exportación individual, adjuntos vinculados, paginación y sincronización.
- **Aceptación:** cambios entre sesiones/dispositivos; reintentos idempotentes; aislamiento probado; borrado/export según política.

### Fase 5 — Memoria avanzada e identidad
- Perfil por cuenta; categorías canónicas; memoria temporal/duradera con procedencia/confianza/sensibilidad/expiración; embeddings opcionales.
- **Aceptación:** ver fuente/influencia, corregir/exportar/olvidar; expiración y borrado probados; no inferir recuerdos sensibles; recuperación medida con corpus.

### Fase 6 — Proveedores, herramientas e investigación
- Adaptadores por modalidad; token/coste/timeout/cancelación/fallback; permisos, confirmación, trazabilidad y contenido externo no confiable.
- **Aceptación:** cambiar proveedor no altera identidad/datos; fallos degradan claramente; argumentos/permiso/límites probados; métricas no contienen contenido privado.

### Fase 7 — Frontend accesible y resistente
- Completar errores/loading, accesibilidad, móvil y CSP. Puede ir en paralelo una vez fijados contratos de fase 2.
- **Aceptación:** E2E escritorio/móvil, teclado/lector, renderer XSS y fallos de red pasan; política de caché visible/verificable.

### Fase 8 — Voz, multimedia, PWA y Android
- Resolver permisos; voz realtime solo con adaptadores; build/firma Android, storage seguro, archivos y permisos runtime; offline gradual.
- **Aceptación:** dispositivos objetivo; permiso bajo acción del usuario; sesión en storage nativo; offline declara límites; sin afirmar IA local no validada.

### Fase 9 — Autonomía y estabilización
- Tras permisos/auditoría de herramientas: scheduler, horarios, pausa/cancelación, límites y propuestas revisables.
- **Aceptación:** propuesta no ejecuta; autorización ligada a acción/alcance/expiración; auditoría y pruebas de abuso; release solo con revisión y reversión.

Fases 1–2 son prerequisito de datos en 4–6. Accesibilidad puede ir en paralelo tras contratos. Android/offline espera sesión/sincronización; autonomía va al final por el impacto de errores de herramientas.

## 11. Prioridades recomendadas

1. Resolver SEC-01, PRV-01, API-01, PRV-02 y PRV-03 antes de ampliar alcance.
2. Corregir búsqueda doble, minimización de queries, categorías y retención local.
3. Añadir pruebas de integración/seguridad que ejerciten riesgos, no solo presencia de código.
4. Definir migraciones y fuente de verdad de conversación antes de refactor de almacenamiento.
5. Modularizar de forma incremental con pruebas de caracterización.
6. Construir memoria avanzada, proveedores multimodales, Android y autonomía sobre contratos verificables.

## 12. Estado al cierre

- Rama auditada: aranza-v1-105-development.
- HEAD: 0fcdadab50779de6ee6d048d1837c7b4bdff742a.
- Estado previo al informe: limpio y sincronizado con remoto.
- main permaneció en otro checkout, limpia, SHA 046827e7441b5f269acfcbc107a1b2b0dfca7205.
- Sin cambios de código, tests locales, commit, push ni despliegue.
- Única modificación autorizada: este informe; Git debe mostrar únicamente este archivo nuevo y no versionado.
- No se reprodujo el perfil personal ni se añadieron secretos, tokens o valores privados.
