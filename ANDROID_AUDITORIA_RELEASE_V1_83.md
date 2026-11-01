# Auditoría estática Android (v1.83)

Se incorpora `verificar_android_release.py`, una comprobación local previa a preparar una compilación Android. Revisa que exista `package.json` privado, que Capacitor tenga identificador/nombre, que WebView no permita contenido mixto ni depuración, y que la plantilla de manifiesto mantenga permisos mínimos, `allowBackup=false` y `usesCleartextTraffic=false`.

## Uso

```bash
python verificar_android_release.py
```

El comando devuelve código de salida distinto de cero si detecta una regresión. No lee ni imprime secretos.

## Límites

Es una auditoría estática de los archivos fuente. No inspecciona el Merged Manifest que producen Gradle y los plugins, no revisa vulnerabilidades transitivas, no verifica certificados TLS, no firma APK, no comprueba almacenamiento Android Keystore y no sustituye pruebas en un Xiaomi/HyperOS real. La sesión continúa usando el mecanismo web documentado en v1.81; Android Keystore todavía no está integrado.

## Siguiente bloque técnico

Antes de distribuir un APK hay que elegir y fijar una versión compatible de un plugin de almacenamiento seguro mantenido para Capacitor, probar su implementación nativa, migrar tokens sin exponerlos a logs y verificar expiración/revocación. No se simula ese comportamiento con almacenamiento web.
