PROYECTO ARANZA v1.15

Novedad: ahora puedes adjuntar TXT, MD, CSV, JSON y PDF con texto seleccionable desde el chat y pedirle a Aranza que analice el archivo.

Uso:
1. Inicia sesión en Aranza.
2. Pulsa el clip (📎) junto al cuadro de mensaje.
3. Selecciona un archivo de hasta 5 MB.
4. Escribe una instrucción, por ejemplo: "Resume los puntos principales", o envíalo sin instrucción para usar el resumen predeterminado.
5. Pulsa enviar.

Los archivos se envían al backend para análisis en memoria; el backend no los guarda en disco ni conserva el texto extraído. La conversación local puede guardar el nombre del archivo y la respuesta, como el resto de los mensajes.

Formatos permitidos: .txt, .md, .csv, .json, .pdf. PDF escaneados sin texto seleccionable aún no funcionan porque no se incluye OCR.

IMPORTANTE:
- Esta es una versión de desarrollo, no desplegada en producción.
- Conserva la versión anterior y haz una copia de seguridad de SQLite antes de actualizar el hosting.
- No sobrescribas tu base de datos ni tu archivo .env.
- El análisis requiere un proveedor/modelo configurado; las llamadas externas pueden tener costo.
