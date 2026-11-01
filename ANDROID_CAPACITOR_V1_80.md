# Preparación Android con Capacitor (v1.80)

Esta entrega incorpora el esqueleto de configuración de Capacitor, pero **no contiene un APK ni el proyecto Android generado**. El backend FastAPI sigue siendo el servidor de autenticación, conversaciones, memoria y herramientas.

## Requisitos

- Node.js LTS y npm.
- Android Studio estable y Android SDK.
- Java/JDK compatible con la versión de Android Gradle Plugin instalada por Capacitor.
- Una URL HTTPS del backend Aranza accesible desde el teléfono.

## Inicialización local (Windows PowerShell)

Desde la carpeta que contiene `package.json`:

```powershell
npm install
npm run cap:add:android
npm run cap:sync
npm run cap:open
```

`cap:add:android` genera la carpeta `android/` en el equipo local. Esa carpeta se excluye del ZIP y del control de versiones para evitar incluir binarios y configuraciones específicas de cada máquina. No ejecutes estos comandos hasta tener Node.js y Android Studio instalados.

## Configurar la URL del backend

El frontend usa `window.ARANZA_API_BASE` si existe; de lo contrario, usa `window.location.origin`. Para una app empaquetada, el origen local del WebView no es el backend. Antes del script principal de `index.html`, define la URL HTTPS real del servidor en un archivo de configuración local no versionado, o adapta el proceso de compilación para inyectarla:

```html
<script src="/aranza-runtime-config.js"></script>
```

Ejemplo de `aranza-runtime-config.js` (no incluir claves secretas):

```js
window.ARANZA_API_BASE = 'https://TU-SERVIDOR-HTTPS';
```

No se debe poner una API key de proveedor en el cliente ni en el APK. El servidor debe gestionar esos secretos.

## CORS y seguridad

- Configura `ARANZA_ALLOWED_ORIGINS` en el backend con el origen exacto que use la versión de Capacitor instalada. En Android suele usarse `https://localhost`, pero verifica el origen efectivo de la versión/configuración generada antes de abrir CORS.
- No uses `*` junto con credenciales.
- Mantén HTTPS, `allowMixedContent: false` y la depuración WebView desactivada en producción.
- No habilites permisos de cámara/micrófono hasta implementar flujos nativos visibles y probarlos.
- No guardes tokens en `localStorage` como solución definitiva para Android. Esta entrega no cambia el mecanismo actual de sesión; la migración a almacenamiento nativo seguro queda pendiente.

## Estado real de esta versión

- Incluye `capacitor.config.ts`, `package.json`, `.gitignore` y esta guía.
- No incluye `android/`, APK, firma, permisos nativos ni plugins de cámara/audio.
- No se ha probado en un dispositivo Xiaomi ni en Android Studio en este entorno.
- La PWA continúa funcionando de forma independiente.
