# v1.83

- Añade auditoría estática de preparación Android (`verificar_android_release.py`).
- Comprueba configuración de Capacitor, depuración/contenido mixto, permisos declarados y políticas de backup/tráfico claro.
- Añade pruebas para detectar regresiones de seguridad en el manifiesto.
- Documenta límites: no genera APK ni integra Keystore; la sesión web no se presenta como almacenamiento nativo seguro.
