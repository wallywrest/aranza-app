# Seguridad de sesión y preflight Android (v1.81)

## Qué incorpora esta versión

- `verificar_android.py` valida la URL HTTPS del backend y los orígenes CORS declarados antes de preparar una compilación móvil.
- Rechaza URLs HTTP, credenciales embebidas, parámetros, fragmentos, comodines y orígenes con rutas.
- No imprime valores de configuración sensibles.
- Añade pruebas automatizadas para casos válidos e inválidos.

## Estado de la sesión

El cliente web actual conserva el token de sesión en `sessionStorage`. Esta versión **no afirma que eso sea almacenamiento nativo seguro** y no cambia el flujo de autenticación existente.

Antes de distribuir un APK se debe integrar un plugin de almacenamiento seguro mantenido y compatible con Capacitor, revisar su implementación Android y guardar allí el token. No usar `localStorage`, Preferences sin cifrado ni archivos de configuración para guardar tokens. Las claves de proveedores permanecen exclusivamente en FastAPI.

## Preparación

Configura en el entorno de compilación:

- `ARANZA_API_BASE=https://tu-backend.example`
- `ARANZA_ALLOWED_ORIGINS` con orígenes HTTPS exactos, separados por comas, incluyendo el origen que use la versión instalada de Capacitor.

Ejecuta `python verificar_android.py`. La herramienta valida configuración declarada, no conectividad, CORS real, certificado TLS, APK ni permisos del teléfono. Verifica el origen efectivo de Capacitor antes de añadirlo a CORS.

## Pendiente antes de APK

1. Plugin de almacenamiento seguro y migración de sesión con pruebas en dispositivo.
2. Renovación/revocación y expiración de sesión comprobadas en Android.
3. Permisos de cámara/micrófono solicitados solo al iniciar cada función.
4. Pruebas en Android real, incluido Xiaomi/HyperOS.
5. Firma de release, revisión de dependencias y política de privacidad.

No se genera APK en esta versión.
