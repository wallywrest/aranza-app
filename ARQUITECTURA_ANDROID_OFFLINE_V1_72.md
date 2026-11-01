# Arquitectura objetivo: Aranza para Android y modo sin conexión

## Objetivo

Preparar una evolución gradual de Aranza desde la PWA actual hacia una aplicación Android instalable, manteniendo el backend y la experiencia web existentes. Esta versión documenta decisiones y límites; **no añade todavía un APK, permisos nativos, ventana flotante ni inferencia local**.

## Arquitectura propuesta

1. **Cliente web/PWA**: interfaz adaptable, conversaciones aisladas por `conversation_id`, adjuntos y estado local temporal. La PWA sigue siendo la base multiplataforma.
2. **Backend FastAPI**: autenticación, persistencia SQLite, coordinación de modelos y herramientas. El backend conserva la autoridad sobre los datos sincronizados.
3. **Adaptador Android (fase posterior)**: empaquetar la PWA con Capacitor. Los plugins nativos se añaden solo cuando una función los necesita; no se duplicará la lógica de conversación.
4. **Servicios locales opcionales**: almacenamiento cifrado de elementos pendientes, transcripción local y un modelo compacto. Se mantienen separados del backend para que la app siga funcionando sin ellos.

## Experiencia Android deseada

- Acceso normal desde el icono de la aplicación.
- Acceso rápido opcional mediante burbuja, mosaico de Ajustes rápidos o acceso lateral compatible con la versión de Android/HyperOS.
- Una ventana superpuesta real requeriría permiso especial de Android (`SYSTEM_ALERT_WINDOW`) y una justificación clara. No se debe solicitar al instalar ni activar sin consentimiento.
- Una burbuja o servicio persistente tiene restricciones adicionales de Android y puede variar por versión y fabricante. No se promete integración como aplicación de sistema ni acceso privilegiado.

## Cámara, imágenes y audio

- Imágenes: selector del sistema como opción predeterminada; cámara mediante captura nativa solo después de solicitar permiso.
- Audio: grabación iniciada por el usuario, indicador visible mientras el micrófono está activo y controles para cancelar/eliminar antes de enviar.
- Transcripción: proveedor remoto cuando hay conexión; motor local opcional cuando exista un modelo compatible descargado.
- No mantener micrófono/cámara activos en segundo plano ni grabar de forma encubierta.

## Modo sin conexión

El modo offline debe tener alcance explícito y degradación elegante:

- Disponible sin red: abrir conversaciones guardadas en el dispositivo, redactar mensajes, consultar notas/documentos descargados y ejecutar un modelo local pequeño si el hardware lo permite.
- Requiere conexión: sincronización entre dispositivos, búsqueda web, modelos remotos y herramientas alojadas en servidor.
- Cola de salida: mensajes pendientes con identificador único, estado visible y reintento seguro al recuperar conexión. Resolver conflictos sin sobrescribir silenciosamente mensajes.
- Descargas: el usuario elige descargar modelos y paquetes de conocimiento; mostrar tamaño, espacio requerido, versión y forma de eliminarlos.
- Los datos locales sensibles deben protegerse con almacenamiento seguro del sistema; no guardar claves de proveedor dentro del APK.

## Fases de implementación y criterios de aceptación

### A. Preparación web (antes de Android)
- Confirmar aislamiento de conversaciones y persistencia por cuenta.
- Estabilizar carga de imágenes y límites de tamaño/tipo.
- Añadir flujo de grabación/transcripción web con permisos y estados visibles.
- Diseñar sincronización idempotente y cola offline antes de conectar un cliente móvil.

### B. PWA instalable
- Manifest, iconos, service worker y estrategia de caché revisados.
- Shell y recursos esenciales disponibles offline; no fingir que el modelo remoto funciona sin red.
- Pruebas de instalación, actualización, pérdida de conexión y recuperación.

### C. Aplicación Android con Capacitor
- Proyecto Android reproducible y firmado para pruebas.
- Selector de imágenes, cámara y grabación con permisos mínimos.
- Pruebas en dispositivo físico y en la versión concreta de Android/HyperOS.

### D. Acceso rápido y superposición
- Evaluar primero burbuja/acceso rápido permitido por Android.
- Implementar superposición solo si el flujo aporta valor, con activación manual, aviso persistente y opción para desactivarla.
- No solicitar permisos de accesibilidad para simular una integración de sistema.

### E. Inteligencia local
- Benchmark de modelos pequeños en el dispositivo real: latencia, RAM, almacenamiento, temperatura y batería.
- Descarga opcional, verificación de integridad, licencia y eliminación sencilla.
- Enrutamiento transparente: modelo local para tareas básicas y remoto para tareas que requieran mayor capacidad.

## Decisiones de seguridad

- Ninguna clave API dentro del cliente web o APK.
- Permisos de cámara/micrófono bajo demanda, nunca por defecto.
- Cifrado para datos locales sensibles y transporte HTTPS para sincronización.
- Controles visibles para exportar y borrar datos locales.
- Actualizaciones firmadas y canal de pruebas separado del despliegue público.

## Fuera del alcance de v1.72

No se crea APK, no se modifica el backend de producción, no se activa una ventana flotante, no se instala un servicio en segundo plano y no se descarga ningún modelo. La versión es una especificación técnica para evitar integrar funciones nativas de forma improvisada.
