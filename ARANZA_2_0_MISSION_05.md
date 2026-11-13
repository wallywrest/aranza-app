# Aranza 2.0 — Misión 05: integridad de conversaciones

## Alcance

Esta etapa mejora el historial remoto y la limpieza del estado local. Mantiene el aislamiento por cuenta y amplía la API existente para que la web y los futuros clientes puedan compartir el mismo contrato.

La Misión 05 implementa el pilar de conversaciones descrito en [ARANZA_2_0_MASTER_SPEC.md](ARANZA_2_0_MASTER_SPEC.md). No reduce ni reemplaza los 14 pilares de Aranza 2.0. La aplicación Android nativa en Kotlin y Jetpack Compose, la voz, la iniciativa supervisada, las integraciones y el resto del ecosistema permanecen en el roadmap.

## Cambios

- Se añadió `conversaciones.archived` con una migración aditiva. Las conversaciones existentes quedan activas (`archived = 0`) sin reescribir sus mensajes.
- `GET /conversations` permite buscar por título o contenido con `q` y consultar el conjunto archivado con `archived=true`. Ambos filtros se aplican dentro de la cuenta autenticada.
- `PATCH /conversations/{id}` permite archivar y reactivar. La vista web tiene búsqueda, filtro de archivadas y acciones de archivo/reactivación.
- La eliminación de la vista web usa `DELETE /conversations/{id}`. El backend elimina mensajes y metadatos dentro de una transacción y mantiene el filtro de cuenta.
- `GET /account/identity` entrega a una sesión válida su identificador estable. La web separa mensajes, metadatos y borradores locales por cuenta.
- Al cerrar sesión, expirar la sesión o cambiar credenciales, la web limpia sus claves locales de Aranza y la identidad de sesión. Una falla transitoria de red conserva el estado local.
- Los análisis de documentos e imágenes aceptan `conversation_id` y guardan en el historial el nombre del adjunto, la instrucción y el resultado. El contenido binario y el texto extraído no se guardan (`stored: false`; `history_saved: true`).
- La exportación v3 incluye el estado de archivo de cada conversación.

## Pruebas y validación local

- Suite focalizada de Misión 05: **24 aprobadas**.
- Suite completa: **366 aprobadas**.
- `compileall`: aprobado.
- Comprobación de sintaxis JavaScript con Node: aprobada.
- CI GitHub Actions para el commit de código `6a165ec`: **Ubuntu + Python 3.11 aprobado** y **Windows + Python 3.11 aprobado** ([workflow](https://github.com/wallywrest/aranza-app/actions/runs/43375951759)).
- Prueba manual en navegador local con backend y modelos simulados: inicio de sesión, chat, búsqueda por título y por nombre de adjunto, archivo/reactivación, lectura del análisis desde el historial, eliminación remota y retorno a la pantalla de acceso al cerrar sesión.
- Los datos de prueba, la base SQLite y el bytecode se mantuvieron en ubicaciones temporales. No se usaron proveedores reales.
- Advertencia no bloqueante: Starlette depreca `TestClient` con `httpx` y recomienda `httpx2`.

El navegador de prueba no permitió leer `localStorage` directamente desde el contexto de automatización. La limpieza al cerrar sesión queda cubierta por el código y las regresiones de contrato del frontend, aunque no se inspeccionó el contenido del almacenamiento después del cierre.

La suite local usó Python 3.15.1 porque es el intérprete disponible en este equipo. La compatibilidad de CI con Python 3.11 quedó validada en Windows y Ubuntu tras publicar la rama. No se hicieron pruebas en el Xiaomi ni se generó un APK.

## Límites y continuidad

- Los adjuntos binarios no se conservan. El historial guarda solo el nombre, la instrucción y el resultado del análisis.
- La búsqueda usa `LIKE` de SQLite y cubre títulos y mensajes de la cuenta; no es una búsqueda semántica.
- No hay una suite Playwright/Selenium configurada en el proyecto. Se validó el flujo en el navegador de forma manual y la integración del backend con `TestClient`.
- La API de conversaciones y la identidad por cuenta sirven como base reutilizable para la app nativa Android; las pruebas de permisos, sincronización entre dispositivos y hardware permanecen pendientes.
- `main`, Render, secretos y configuración de producción no se modificaron.
