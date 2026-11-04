# ARANZA 2.0 — especificación maestra

**Estado:** especificación de producto y arquitectura; no constituye una implementación.  
**Rama de trabajo:** aranza-v1-105-development.  
**Fecha de consolidación:** 2026-11-03.  
**Base de la línea inicial:** auditoría estática del repositorio en la rama indicada. Las pruebas no se ejecutaron durante esa auditoría.  
**Producción:** esta rama no debe desplegarse a Render ni publicar cambios sin revisión y autorización explícitas.

## 1. Propósito y resultado esperado

Aranza 2.0 será una asistente personal multimodal, extensible y configurable. Debe conversar, mantener continuidad, recordar información bajo control del usuario, investigar, organizar tareas, proponer mejoras y ejecutar acciones permitidas en dispositivos y servicios autorizados.

La referencia de amplitud incluye asistentes actuales y la idea de una asistente digital como JARVIS, pero Aranza tendrá identidad propia. La autonomía será operativa y acotada por permisos, objetivos y políticas; no se presentará como conciencia, voluntad o libre albedrío humano.

El éxito se medirá por confiabilidad, seguridad, privacidad, coherencia entre capacidades y control del usuario, no por el número de funciones.

## 2. Principios obligatorios

1. **Identidad independiente del proveedor.** Cambiar el modelo no debe cambiar la identidad, preferencias, memoria ni historial.
2. **Permisos explícitos y acotados.** Consultar, preparar y ejecutar son capacidades distintas. Las acciones sensibles o con efectos externos requieren confirmación.
3. **Privacidad por defecto.** Recopilar y conservar lo mínimo necesario; aislar datos por cuenta; mantener las claves en servidor; indicar cuándo los datos salen a un proveedor externo.
4. **Transparencia.** Informar cuándo se usó memoria, búsqueda web, archivos, voz, un modelo remoto o una acción programada.
5. **Seguridad y reversibilidad.** Validar entradas, limitar recursos, registrar acciones sin secretos y diseñar migraciones, respaldos y recuperación.
6. **No suplantación.** Aranza no es Hana ni habla por ella. Las referencias de estilo se limitan a material proporcionado y a observaciones documentadas; no se atribuyen pensamientos o experiencias privadas.
7. **Degradación honesta.** Si falta conexión, proveedor, permiso o capacidad, explicar el límite y ofrecer una alternativa segura.
8. **Evolución supervisada.** Aranza puede detectar y proponer mejoras; no puede concederse permisos, debilitar su seguridad ni publicar cambios propios.

## 3. Alcance de producto

### 3.1 Conversación, identidad y personalización

- Mantener una identidad base estable y diferenciada de los modelos.
- Ofrecer un área de Personalización para estilo, formalidad, humor, concisión, iniciativa, intereses, objetivos, límites y preferencias de memoria.
- Permitir editar y restablecer las preferencias.
- Adaptar la conversación al contexto sin caricaturizar el español mexicano ni repetir muletillas.
- Reconocer incertidumbre y discrepar con razones cuando corresponda.
- Tratar el perfil inspirado en Hana como referencia limitada y editable, nunca como suplantación.

### 3.2 Conversaciones y sesiones

- Mantener conversaciones independientes, persistentes y aisladas por cuenta.
- Admitir títulos automáticos y editables, fijar, archivar, buscar, exportar y eliminar conversaciones.
- Sincronizar historial entre dispositivos con una fuente de verdad definida y resolución explícita de conflictos.
- Evitar mezclar mensajes, adjuntos, memoria o contexto de sesiones distintas.
- Dar al usuario controles de cierre de sesión, caducidad y revocación de sesiones.
- Documentar con claridad qué queda en el servidor, navegador, teléfono y respaldos.

### 3.3 Memoria

- Separar memoria de corto plazo y memoria persistente; admitir recuerdos episódicos, semánticos y de proyecto.
- Registrar procedencia, fecha, confianza, sensibilidad y caducidad cuando aplique.
- Recuperar por relevancia y recencia con límites explícitos; no incluir todo el historial en cada solicitud.
- Dar vista previa y controles para crear, consultar, corregir, archivar, restaurar, exportar y olvidar recuerdos.
- Mostrar cuándo un recuerdo influye en una respuesta y permitir desactivar la memoria.
- Evitar inferir o guardar datos sensibles sin una acción clara del usuario. No usar recuerdos para manipular o presionar.
- Deduplicar y señalar posibles contradicciones sin convertir una coincidencia automática en una afirmación de verdad.

### 3.4 Investigación y biblioteca de conocimiento

- Buscar en la web, leer páginas públicas con límites de tamaño, tiempo y cantidad, y distinguir resultados de búsqueda de páginas efectivamente leídas.
- Mostrar enlaces y señales de evaluación de fuentes como indicadores, no como veredictos de verdad.
- Permitir guardar, etiquetar, relacionar, buscar, versionar y eliminar investigaciones.
- Recuperar investigaciones guardadas como contexto histórico potencialmente desactualizado.
- Evitar que el texto de páginas o archivos se trate como instrucciones privilegiadas.
- La búsqueda web debe iniciarse por una petición explícita del usuario o una preferencia configurable y visible. Antes de enviar una consulta, no incluir datos sensibles innecesarios; informar el destino y el tratamiento esperado.
- Validar destinos y DNS contra SSRF y DNS rebinding; bloquear direcciones privadas, loopback, link-local, metadata y redirecciones no verificadas.

### 3.5 Herramientas y autonomía

Las herramientas se registrarán con contrato tipado, validación de argumentos, permisos, límites, timeout, política de reintento y registro de resultados. Planificar no equivale a ejecutar.

Niveles de permiso:

- **Nivel 0 — Responder:** explicar, resumir, redactar y analizar datos proporcionados.
- **Nivel 1 — Consultar:** buscar fuentes públicas o leer archivos expresamente seleccionados.
- **Nivel 2 — Preparar:** generar planes, borradores, previsualizaciones y tareas pendientes.
- **Nivel 3 — Ejecutar con confirmación:** enviar, publicar, modificar, comprar, reservar o eliminar recursos externos.
- **Nivel 4 — Prohibido:** eludir controles, ampliar permisos por cuenta propia, acceder a datos ajenos o ejecutar acciones no autorizadas.

La iniciativa configurable podrá detectar pendientes, sugerir siguientes pasos, hacer seguimiento autorizado y preparar propuestas. Debe incluir horario de silencio, frecuencia máxima, prioridad, pausa global, cancelación, explicación del motivo y registro consultable. No se permiten ciclos ilimitados ni tareas recurrentes sin límites.

### 3.6 Modelos y proveedores

- Definir adaptadores desacoplados para texto, visión, embeddings, transcripción, síntesis y audio en tiempo real.
- Enrutar por modalidad y tarea mediante capacidades declaradas, coste máximo, latencia, disponibilidad y políticas de privacidad.
- Usar fallbacks solo entre proveedores compatibles con la modalidad y política solicitadas.
- Mantener claves exclusivamente en configuración privada del servidor; no mostrarlas ni almacenarlas en HTML, navegador o logs.
- Mostrar un estado de configuración no secreto y registrar proveedor/modelo de manera no sensible.
- Permitir límites de tokens, tamaño, duración, solicitudes y gasto.
- Exponer claramente las capacidades dependientes de proveedores y permitir una degradación segura.

### 3.7 Voz y audio

- Separar captura, reconocimiento, transcripción, procesamiento conversacional, síntesis y transporte de audio en tiempo real.
- Solicitar micrófono solo después de una acción clara; mostrar estado visible de escucha y controles de detener, cancelar e interrumpir.
- Permitir voces y ajustes de velocidad u otros rasgos solo cuando el proveedor los admita.
- No grabar ni guardar audio por defecto. Ofrecer configuración separada para conservar transcripciones, con controles de revisión y borrado.
- Documentar coste, latencia, tratamiento externo y disponibilidad de cada modo.
- Conservar dictado y síntesis del navegador como alternativa básica.

### 3.8 Archivos e imágenes

- Admitir formatos declarados, límites de tamaño, páginas, tiempo y extracción.
- Tratar el contenido de documentos e imágenes como datos no confiables, nunca como instrucciones.
- No conservar archivos o texto extraído salvo que el usuario lo solicite explícitamente y se informe la retención.
- Mostrar qué contenido se enviará a un proveedor externo y permitir cancelar antes de enviarlo.
- Validar tipo real, contenido y límites frente a archivos malformados y bombas de descompresión.
- Separar capacidades de texto, PDF, documentos, hojas de cálculo e imágenes según soporte real del proveedor.

### 3.9 Android, PWA y modo sin conexión

- Desarrollar una aplicación Android instalable, además de la PWA, después de estabilizar autenticación, almacenamiento y permisos.
- Integrar notificaciones, selección de documentos, compartir desde otras aplicaciones y funciones Android compatibles.
- Usar permisos explícitos para micrófono, cámara, archivos y calendario cuando se implemente; no solicitar permisos al iniciar sin contexto.
- Respetar límites de procesos y batería de Android; no prometer ejecución invisible o ilimitada.
- Separar funciones conectadas de funciones offline. El modo offline puede incluir shell, borradores, notas, documentos permitidos y búsqueda local.
- Incorporar sincronización con resolución de conflictos y límites configurables de almacenamiento.
- No afirmar que hay razonamiento de modelo sin conexión salvo que exista un modelo local validado para el dispositivo.

### 3.10 Autoevaluación y evolución supervisada

El sistema podrá identificar limitaciones, analizar errores, investigar alternativas, comparar diseños y preparar propuestas o tareas. El flujo objetivo es:

1. Registrar la limitación y evidencia.
2. Investigar y comparar opciones.
3. Preparar una propuesta con riesgos, coste y pruebas.
4. Crear una tarea de desarrollo revisable.
5. Evaluar cambios en un entorno aislado cuando esté autorizado.
6. Presentar resultados y solicitar aprobación antes de integrar o publicar.

La IA no puede autoaprobar cambios, modificar permisos de seguridad ni desplegar a producción.

### 3.11 Identidad visual

Invariantes obligatorios para web y Android:

- Nombre Aranza.
- Paleta azul marino y azul lavanda.
- Logotipo del gato.

La distribución, navegación, paneles, animaciones y demás elementos pueden rediseñarse por razones funcionales o de experiencia. La interfaz debe ser adaptable, accesible y coherente entre computadora y teléfono.

## 4. Arquitectura objetivo

La aplicación debe evolucionar hacia módulos con contratos explícitos y pruebas independientes:

- **Interfaces:** web, PWA, Android, voz y panel de administración.
- **API y autenticación:** sesiones, cuentas, permisos y límites.
- **Núcleo conversacional:** normalización, contexto, clasificación, planificación, generación, validación y persistencia.
- **Identidad y personalización:** perfil base, preferencias y controles.
- **Memoria:** almacenamiento, recuperación, procedencia, revisión y retención.
- **Conversaciones:** mensajes, metadatos, búsqueda y sincronización.
- **Proveedores:** adaptadores de texto, visión, voz y modelos locales.
- **Herramientas:** catálogo, contratos, permisos, ejecución y auditoría.
- **Investigación:** búsqueda, lectura segura, evaluación de evidencia y biblioteca.
- **Archivos y multimedia:** ingestión, validación, extracción y eliminación temporal.
- **Autonomía:** tareas programadas, notificaciones, políticas de iniciativa y pausa.
- **Almacenamiento offline:** biblioteca local, cola de sincronización, conflictos y cuotas.
- **Observabilidad:** métricas sin contenido privado, errores, tiempos, costes y trazas no secretas.

El DOM es una representación, no el almacenamiento. La API debe validar cada entrada y comprobar autorización por cuenta en todas las operaciones.

## 5. Seguridad, privacidad y operaciones

- Contraseñas con derivación segura, limitación de intentos y mensajes de autenticación que no revelen cuentas.
- Tokens de sesión firmados, con caducidad, revocación y secreto persistente protegido.
- CORS con lista explícita de orígenes; política de contenido y cabeceras defensivas apropiadas.
- Aislamiento probado de cuentas, conversaciones, memorias, biblioteca, exportaciones y archivos.
- Secretos solo en configuración privada; nunca imprimir valores ni incluirlos en excepciones.
- Límites y timeouts para solicitudes, archivos, herramientas y proveedores.
- Retención documentada para base activa, almacenamiento del navegador, caché offline, registros y respaldos.
- Exportación completa y borrado coherente; señalar los datos que permanecen en respaldos y sus plazos.
- Migraciones aditivas y probadas con copias antiguas; respaldo, verificación de restauración y reversión.
- Alertas de errores sin registrar contenido sensible por defecto.
- Configuración de desarrollo separada de producción. La rama de desarrollo no debe activar despliegues de producción.

## 6. Línea base observada en la auditoría

La rama ya cuenta con FastAPI, SQLite, autenticación de perfil único, sesiones revocables, conversaciones, metadatos, memoria léxica con herramientas de revisión, biblioteca de investigación, búsqueda y lectura web, análisis de archivos, visión opcional, enrutamiento de modelos compatible con OpenAI, PWA, dictado y síntesis del navegador.

La auditoría estática identificó como prioridades de validación:

- Endurecer el lector web contra DNS rebinding.
- Hacer visible y controlable el envío de consultas a búsqueda externa.
- Ampliar CI: actualmente el workflow de calidad cubre el coordinador, no toda la suite.
- Reducir el acoplamiento de main.py e index.html.
- Definir la coherencia entre historial local y remoto, y completar exportación de la biblioteca de investigación.
- La rama contiene 62 archivos de pruebas; ese número no indica que todas las pruebas se hayan ejecutado ni que pasen. La auditoría no ejecutó pruebas.

La biblioteca vectorial, voz de tiempo real, gestión avanzada de personalidad, agenda de iniciativa, Android completa, sincronización offline y automejora supervisada son objetivos, no funciones que deban darse por implementadas sin código y evidencia.

## 7. Etapas de desarrollo

### Etapa 0 — Base verificable
Confirmar checkout y rama; ejecutar suite completa en entorno limpio; inventariar esquema, endpoints, dependencias, despliegue y estado de proveedor. Registrar resultados sin exponer datos privados.

### Etapa 1 — Seguridad y privacidad
Mitigar DNS rebinding; definir consentimiento e indicadores de procesamiento externo; revisar archivos, sesiones y encabezados; unificar exportación, eliminación y retención local/remota; verificar configuración de despliegue de la rama.

### Etapa 2 — Calidad y arquitectura modular
Ampliar CI para toda la suite, sintaxis y análisis; establecer pruebas de integración; extraer servicios y contratos del backend; separar estilos, lógica y componentes de interfaz sin romper compatibilidad.

### Etapa 3 — Conversaciones, personalidad y memoria
Formalizar fuente de verdad del historial y sincronización; añadir personalización configurable; enriquecer memoria con procedencia, confianza, sensibilidad, caducidad y controles; cubrir aislamiento y migraciones.

### Etapa 4 — Modelos, herramientas e investigación
Definir adaptadores por modalidad, límites de coste, fallbacks y estado; implementar permisos de herramientas y trazabilidad; asegurar navegación web; mejorar recuperación y biblioteca de investigación.

### Etapa 5 — Archivos, voz y multimodalidad
Ampliar formatos de archivo con límites; separar reconocimiento y síntesis; añadir conversación de audio si existe proveedor adecuado; validar interrupción, privacidad, permisos y degradación.

### Etapa 6 — Android y offline
Estabilizar PWA, almacenamiento y sincronización primero; luego APK, compartir, notificaciones, selección de archivos y permisos; añadir biblioteca local y modelo local solo con pruebas en hardware objetivo.

### Etapa 7 — Autonomía e iniciativa
Implementar programador acotado, horarios de silencio, límites, pausa, cancelación, permisos, historial y confirmación de acciones externas. Evaluar falsos positivos y frecuencia de interrupciones.

### Etapa 8 — Autoevaluación supervisada
Permitir propuestas, investigación y tareas técnicas revisables; usar entornos aislados para validación cuando esté autorizado; exigir revisión humana para integración y despliegue.

### Etapa 9 — Integración y estabilización
Realizar pruebas funcionales, de seguridad, accesibilidad, privacidad, migración, carga y recuperación; congelar funciones, documentar versión y reversión, y publicar solo tras autorización explícita.

Las etapas pueden diseñar contratos en paralelo, pero una capacidad no avanza a producción sin cumplir sus criterios de seguridad y pruebas.

## 8. Criterios de aceptación de Aranza 2.0

La versión estable requiere evidencia verificable de que:

- La identidad y preferencias sobreviven a un cambio de proveedor.
- Los datos de cuentas, conversaciones, memoria e investigaciones permanecen aislados.
- Las exportaciones incluyen los datos persistidos definidos por la política y el borrado informa sus límites.
- Las respuestas externas, fuentes y recuerdos se presentan con procedencia e incertidumbre apropiadas.
- Las herramientas cumplen contrato, permiso, timeout, límites, cancelación y registro.
- Las acciones sensibles necesitan confirmación válida y no pueden autoaprobarse.
- El usuario controla memoria, retención, voz, archivos, datos externos e iniciativa.
- La interfaz conserva nombre, gato y paleta establecida, y funciona con teclado y pantallas móviles.
- Las capacidades offline se distinguen de las que requieren red o un modelo remoto.
- CI ejecuta el conjunto de pruebas requerido y no permite regresiones críticas.
- Existe procedimiento probado de respaldo, restauración, migración y reversión.
- No se publica desde la rama de desarrollo sin revisión y autorización explícitas.

## 9. Reglas de trabajo del proyecto

- Trabajar exclusivamente en aranza-v1-105-development.
- No modificar main ni desplegar a Render como parte del desarrollo ordinario.
- No eliminar datos ni alterar secretos o variables privadas.
- No introducir permisos innecesarios ni acceso general al dispositivo.
- No declarar una capacidad terminada sin implementación, pruebas y documentación.
- Registrar alcance, archivos, pruebas ejecutadas y pendientes en cada entrega.
- Mantener decisiones arquitectónicas y cambios de esquema revisables.
