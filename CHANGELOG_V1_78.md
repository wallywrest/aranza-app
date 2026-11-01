# Aranza v1.78

## Borradores locales y estado de conexión

- El texto escrito en el compositor se guarda como borrador local por cuenta (nombre de usuario del formulario) y conversación.
- Al volver a abrir una conversación o iniciar un chat nuevo, se restaura únicamente el borrador correspondiente.
- Los borradores se eliminan del almacenamiento local cuando el mensaje se completa correctamente; si falla la petición, el texto permanece disponible para recuperarlo.
- El borrador nunca se envía automáticamente al recuperar conexión. El usuario decide cuándo enviarlo.
- Se muestra el estado en línea/sin conexión y se actualiza con los eventos del navegador.
- No se almacenan tokens, archivos adjuntos, mensajes del servidor ni respuestas autenticadas en este mecanismo.

Los borradores contienen texto privado y se guardan en localStorage del navegador de ese dispositivo. No se sincronizan entre dispositivos. Quien tenga acceso al perfil del navegador podría verlos; cerrar sesión no borra los borradores. Para eliminarlos, borra el texto del compositor correspondiente o los datos del sitio desde el navegador.

## Límites

Esta versión no implementa una cola de envío automática ni sincronización offline. Las peticiones al servidor y el uso del modelo siguen requiriendo conexión. El identificador de cuenta usado para separar borradores es el nombre de usuario introducido en el formulario, no una credencial de autenticación.
