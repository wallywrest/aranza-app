ARANZA v1.10 - AJUSTES DE CUENTA Y SEGURIDAD WEB

NOVEDADES
- Puedes cambiar el nombre de usuario desde el menú lateral.
- Para cambiarlo, Aranza solicita la contraseña actual.
- Al cambiar el usuario, todas las sesiones se revocan y debes iniciar sesión con el usuario nuevo.
- Se agregan encabezados de seguridad web y se evita almacenar en caché las respuestas de rutas sensibles.
- HSTS se añade cuando la petición usa HTTPS.

INSTALACIÓN
1. Conserva una copia de seguridad de la base SQLite y de los archivos actuales.
2. Descomprime el parche y sustituye los archivos incluidos en tu proyecto.
3. No sobrescribas tu base de datos SQLite ni el archivo .env.
4. Prueba primero en un entorno de copia.
5. Ejecuta: python -m pytest -q

IMPORTANTE
- Este parche no se ha desplegado a producción.
- Continúa siendo una sola cuenta configurada.
- No hay recuperación por correo; hace falta diseñarla con verificación segura.
