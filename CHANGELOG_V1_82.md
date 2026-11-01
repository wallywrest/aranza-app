# v1.82

- Añadida plantilla mínima de AndroidManifest para la futura app Capacitor.
- Definida política de permisos de cámara y micrófono: uso voluntario, solicitud contextual y sin grabación en segundo plano.
- Se evita pedir acceso amplio al almacenamiento; se recomienda el selector de fotos del sistema.
- Deshabilitados tráfico HTTP sin cifrar y respaldo automático Android de datos privados.
- Añadidas pruebas automatizadas del manifiesto.

No se genera APK, no se solicita ningún permiso en ejecución y no se implementa todavía almacenamiento nativo seguro de sesiones.
