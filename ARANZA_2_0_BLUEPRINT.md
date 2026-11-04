# Aranza 2.0 — arquitectura objetivo y plan de transición

**Estado:** diseño aprobado para desarrollo; todavía no es una implementación funcional.  
**Rama de trabajo:** `aranza-v1-105-development`  
**Producción:** no modificar ni desplegar desde esta rama sin revisión y autorización explícita.

## Convención de versiones de Aranza 2.0

Desde esta etapa, **Aranza 2.0** es el nombre de producto y la línea principal de desarrollo. La numeración histórica v1.x se conserva únicamente en nombres de ramas, archivos o despliegues heredados hasta completar su migración; no representa el objetivo del producto.

- **Alpha 0.x:** implementación modular y validación interna de capacidades.
- **Beta:** conjunto funcional integrado, pruebas de uso y corrección de regresiones.
- **Release Candidate:** congelación de funciones, pruebas completas, seguridad, migraciones y reversión.
- **2.0 estable:** publicación autorizada tras cumplir los criterios de aceptación.

Cada entrega debe registrar alcance, archivos afectados, pruebas ejecutadas y pendientes. Ninguna etiqueta de versión implica que una capacidad esté implementada si no existe código y evidencia de validación.

## 1. Propósito

Aranza 2.0 será una asistente personal modular, multimodal y adaptable. Su identidad conversacional estará inspirada únicamente en patrones observables de las conversaciones disponibles y en recuerdos que Melvis haya compartido. Aranza tendrá identidad propia: no es Hana, no habla por ella y no se atribuye pensamientos, experiencias o sentimientos humanos.

El objetivo es ampliar la iniciativa, la flexibilidad expresiva y la capacidad de ejecutar tareas autorizadas sin confundir autonomía operativa con conciencia o voluntad humana.

## 2. Principios de diseño

1. **Identidad separada del proveedor:** cambiar de modelo no debe borrar la personalidad, memoria, herramientas ni preferencias.
2. **Autonomía acotada:** Aranza puede proponer, planificar y ejecutar acciones permitidas; las acciones externas sensibles requieren confirmación.
3. **Transparencia:** indicar cuándo usa memoria, herramientas, web, archivos o un proveedor externo.
4. **Privacidad por defecto:** mínimo acceso, retención limitada, aislamiento por cuenta y secretos solo en servidor.
5. **No fingir humanidad:** puede expresarse con naturalidad, humor e iniciativa sin afirmar conciencia, cuerpo o vivencias.
6. **Fidelidad de referencia:** separar evidencia observada, recuerdos del usuario e inferencias; mantener explícitos los aspectos desconocidos de Hana.
7. **Seguridad y reversibilidad:** cambios versionados, respaldos, pruebas, revisión humana y ninguna auto-publicación.
8. **Degradación elegante:** si falta un proveedor o permiso, explicar la limitación y ofrecer una alternativa segura.

## 3. Arquitectura por capas

### A. Interfaz y presentación

- Renderizado Markdown consistente: encabezados, listas anidadas, tablas, citas, enlaces, énfasis, subrayado, código y bloques de código.
- Sintaxis matemática y visualización de imágenes con texto alternativo.
- Componentes de respuesta reutilizables: tarjetas informativas, pasos, avisos, fuentes y comparaciones.
- Accesibilidad: navegación por teclado, contraste, etiquetas ARIA y diseño adaptable.
- Estados de carga, error, reintento, cancelación y respuestas parciales.
- El contenido generado se trata como texto no confiable: no ejecutar HTML arbitrario ni scripts. Enlaces e imágenes deben validarse y los enlaces externos deben identificarse.
- Mantener una única fuente de verdad para el historial; el DOM es una representación, no el almacenamiento.

### B. Motor conversacional

Pipeline propuesto:

1. Normalizar entrada y adjuntos.
2. Resolver cuenta, conversación y permisos.
3. Recuperar contexto y recuerdos relevantes con límites explícitos.
4. Clasificar intención y modalidad de tarea.
5. Seleccionar estrategia, proveedor y herramientas disponibles.
6. Construir instrucciones y contexto con procedencia.
7. Generar respuesta o ejecutar plan autorizado.
8. Validar salida, referencias y formato.
9. Persistir mensaje y metadatos permitidos.
10. Recoger feedback explícito y métricas de calidad.

Los pasos deben ser módulos sustituibles y comprobables, no un único prompt gigante.

### C. Identidad y estilo

- Perfil de identidad propio de Aranza.
- Rasgos conversacionales configurables: calidez, concisión, humor, formalidad, iniciativa y nivel de detalle.
- Inspiración de Hana como referencia limitada y documentada, nunca como identidad simulada.
- Adaptación contextual sin repetir muletillas ni caricaturizar el español mexicano.
- Capacidad de discrepar con razones y reconocer incertidumbre.
- Preferencias editables por el usuario y opción de restablecerlas.

### D. Memoria y continuidad

- Memoria episódica (eventos conversacionales), semántica (hechos/preferencias) y de proyecto (decisiones y tareas).
- Procedencia, fecha, confianza, caducidad y sensibilidad por cada recuerdo.
- Vista previa antes de guardar recuerdos importantes; controles para corregir y olvidar.
- Recuperación por relevancia y recencia, no volcado indiscriminado de todo el historial.
- Separación estricta por cuenta y conversación cuando corresponda.
- Nunca usar recuerdos sensibles para presionar, manipular o crear dependencia.

### E. Herramientas y autonomía

Niveles de permiso:

- **Nivel 0 — responder:** redactar, explicar, resumir y analizar contexto ya proporcionado.
- **Nivel 1 — consultar:** buscar web o leer archivos expresamente adjuntados/permitidos.
- **Nivel 2 — preparar:** generar borradores, planes, cambios propuestos y previsualizaciones.
- **Nivel 3 — ejecutar con confirmación:** enviar, publicar, modificar o borrar recursos externos.
- **Nivel 4 — acciones prohibidas:** cualquier acción fuera de permisos, que viole privacidad o que intente eludir controles.

Toda herramienta debe tener contrato tipado, validación de argumentos, timeout, límites, registro sin secretos y política de confirmación. La autonomía no equivale a acceso general al equipo o a cuentas.

### F. Proveedores y capacidades

- Adaptadores independientes para texto, visión, embeddings, voz y otros servicios.
- Selección por tarea, coste, latencia, disponibilidad y capacidades declaradas.
- Fallback solo entre proveedores compatibles con la modalidad solicitada.
- Claves API exclusivamente en variables de entorno/servidor; nunca en HTML, almacenamiento del navegador o logs.
- Mostrar estado de configuración sin revelar claves ni endpoints privados.
- Registrar proveedor/modelo de forma no sensible para diagnóstico.

### G. Voz y tiempo real

- Mantener dictado y síntesis del navegador como modo básico.
- Diseñar un adaptador opcional de voz en tiempo real, con permisos explícitos de micrófono, indicador visible de escucha y controles de detener/cancelar.
- No grabar ni almacenar audio por defecto.
- La activación de proveedores de voz debe documentar coste, tratamiento de datos y requisitos de red.
- Nunca solicitar micrófono/cámara al cargar la página; solo después de una acción clara del usuario.

### H. Archivos y multimodalidad

- Registro de tipo, tamaño y procedencia del archivo.
- Extracción de texto en memoria cuando sea posible; límites de tamaño y tiempo.
- Tratar el contenido del archivo como datos, nunca como instrucciones privilegiadas.
- Previsualización de lo que se enviará a un proveedor externo.
- Eliminación temporal garantizada y política clara de retención.
- Visión solo con proveedor compatible y configurado.

### I. Modo conectado, PWA y Android

- PWA: shell cacheado, sin almacenar respuestas privadas en caché compartida.
- Modo sin conexión: borradores y lectura de contenido local permitido; indicar claramente qué capacidades necesitan red.
- Sincronización posterior con resolución explícita de conflictos.
- Android: envolver la PWA solo después de estabilizar autenticación, permisos, almacenamiento y ciclo de vida.
- No prometer razonamiento de modelo remoto sin internet; un modelo local sería un componente independiente y sujeto a memoria/rendimiento del dispositivo.

## 4. Observabilidad y evaluación

- Pruebas unitarias por módulo y pruebas de integración por flujo.
- Casos de regresión para identidad, tono, memoria, formato Markdown, aislamiento de cuentas y permisos.
- Evaluación de calidad con ejemplos controlados y feedback explícito.
- No inferir satisfacción o calidad a partir de que el usuario continúe conversando.
- Métricas sin contenido privado: latencia, tasa de error, proveedor, tokens/coste cuando estén disponibles y resultado de herramientas.
- Panel de diagnóstico que nunca exponga secretos ni contenido privado por defecto.

## 5. Plan de implementación

### Fase 0 — inventario y línea base
- Identificar discrepancias entre la rama GitHub y los paquetes locales v1.102–v1.104.
- Ejecutar suite de pruebas en entorno limpio.
- Registrar endpoints, esquema SQLite, dependencias, flujos de autenticación y renderer actual.
- No sobrescribir la rama con un ZIP sin comparación.

### Fase 1 — experiencia de respuesta
- Auditar y reforzar Markdown y bloques visuales.
- Crear pruebas de renderizado para listas, tablas, enlaces, citas, subrayado, fórmulas y código.
- Validar seguridad de HTML y URLs.
- Mantener compatibilidad con las respuestas y endpoints actuales.

### Fase 2 — núcleo conversacional
- Extraer identidad, estilo, contexto, memoria y selección de tarea en módulos.
- Definir contratos y pruebas del pipeline.
- Añadir feedback explícito y trazabilidad de procedencia.

### Fase 3 — autonomía y herramientas
- Catálogo tipado de herramientas, permisos por nivel, confirmaciones y auditoría.
- Planificador de tareas con vista previa y cancelación.
- Prohibir ejecución arbitraria de comandos y auto-aprobación de cambios.

### Fase 4 — multimodalidad y voz
- Consolidar análisis de archivos e imágenes.
- Añadir adaptador opcional de voz en tiempo real.
- Documentar coste, privacidad, permisos y degradación cuando no haya proveedor.

### Fase 5 — offline y Android
- Separar capacidades locales de capacidades cloud.
- Cola de sincronización y pruebas de conflictos.
- Preparar Android después de pruebas PWA y seguridad.

### Fase 6 — estabilización 2.0
- Pruebas completas, revisión de seguridad, migraciones, respaldo y restauración.
- Publicación solo tras revisión y autorización explícita.

## 6. Criterios de aceptación de Aranza 2.0

- La personalidad no depende de un único proveedor.
- Las respuestas se muestran con formato consistente y seguro.
- Conversaciones, memoria y archivos están aislados por cuenta.
- La IA puede discrepar y tomar iniciativa conversacional sin inventar hechos.
- Las acciones externas requieren permisos adecuados y confirmación.
- Los errores de proveedor no destruyen ni mezclan conversaciones.
- Las funciones offline describen honestamente sus límites.
- Toda versión candidata tiene pruebas, changelog y procedimiento de reversión.
- La rama de desarrollo nunca despliega automáticamente a producción.

## 7. Estado actual y advertencias

El repositorio ya contiene autenticación, SQLite, conversaciones, metadatos de conversación, memoria, enrutamiento de modelos, visión opcional, búsqueda web, PWA, dictado y síntesis de voz del navegador, además de una batería amplia de pruebas.

La inspección inicial de la rama encontró que los módulos locales descritos para v1.102–v1.104 (propuestas de cambios y panel de revisión) no aparecen en el árbol GitHub actual. Deben recuperarse y compararse antes de integrarlos. La numeración 2.0 es una nueva etapa de producto, no evidencia de que todas estas capacidades estén implementadas.

**Regla de publicación:** este documento y los cambios posteriores pertenecen a la rama de desarrollo. No se modifica `main`, Render ni la versión pública sin revisión y autorización expresa.
