PROYECTO ARANZA v1.19

Esta entrega añade un lector limitado de páginas web públicas en el backend.

Endpoint autenticado:
POST /tools/read-webpage
JSON: {"url":"https://example.com/articulo"}

Admite páginas HTML/XHTML públicas. No ejecuta JavaScript, no sigue redirecciones y limita la descarga y la extracción de texto. El contenido de páginas externas debe tratarse como información no confiable.

No instales el parche sobre una instancia real sin respaldar primero la base de datos y revisar la configuración. Esta entrega no ha sido desplegada ni validada en el hosting del usuario. Las pruebas locales usan transportes simulados para no depender de páginas externas.

Limitaciones: sin OCR, JavaScript, inicio de sesión, CAPTCHA ni botón en la interfaz para esta herramienta. El control DNS no elimina por completo el riesgo de DNS rebinding en entornos hostiles; usa aislamiento de red en despliegues públicos.
