# Android: política de permisos (v1.82)

Esta versión define una plantilla de manifiesto para la futura app Capacitor. **No es un APK ni reemplaza el manifiesto que genera Capacitor**; al crear `android/`, integra y revisa estas declaraciones en `android/app/src/main/AndroidManifest.xml`.

## Permisos mínimos

- `INTERNET`: necesario para comunicarse con FastAPI por HTTPS.
- `CAMERA`: declarar ahora, pero solicitar en tiempo de ejecución solo después de que la persona toque la acción de abrir cámara. Si se usa el selector del sistema para elegir fotos, no pedir permiso general de galería.
- `RECORD_AUDIO`: solicitar solo cuando la persona inicie explícitamente una grabación. Mostrar estado de grabación y ofrecer detener/cancelar.
- Cámara y micrófono se marcan como hardware opcional para no excluir dispositivos sin esos componentes.

No declarar permisos amplios de almacenamiento, lectura de todos los medios, contactos, ubicación, SMS, llamadas ni ejecución permanente en segundo plano. No iniciar cámara/micrófono al abrir la app. No grabar en segundo plano.

## Seguridad

- `allowBackup=false` evita incluir datos privados de la app en respaldos Android por defecto; revisar cualquier política de exportación propia antes de producción.
- `usesCleartextTraffic=false`: no permitir HTTP sin cifrar. El backend debe usar HTTPS válido.
- No incluir claves de proveedores, contraseñas ni tokens permanentes en el APK.
- La plantilla no implementa todavía almacenamiento nativo de tokens. Hasta que se integre y pruebe un almacén seguro, conservar el flujo web existente y no afirmar que los tokens están protegidos por Android Keystore.

## Verificación

Después de generar la plataforma, inspeccionar el manifiesto combinado (Merged Manifest) en Android Studio y comprobar que plugins/dependencias no hayan agregado permisos inesperados. Probar concesión, denegación y revocación de cámara/micrófono en un dispositivo real. Esta plantilla no solicita permisos por sí sola.
