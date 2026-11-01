# Aranza v1.76

## Dictado y lectura en voz alta desde el navegador

- Se añade un control de dictado con `SpeechRecognition` / `webkitSpeechRecognition` cuando el navegador lo admite.
- El dictado usa `es-MX`, muestra estado activo y permite detener el reconocimiento.
- Se añade lectura en voz alta por mensaje de Aranza con `speechSynthesis`.
- La voz se procesa en el navegador: no se sube ni almacena audio en el backend.
- Se limita el texto enviado al motor de voz a 12.000 caracteres y se cancela la reproducción anterior antes de iniciar otra.
- Si el navegador no ofrece estas API, la interfaz informa de la limitación y conserva el uso por texto.

## Límites y privacidad

La disponibilidad y el tratamiento del audio dependen del navegador y del sistema operativo. Algunos navegadores pueden enviar el audio a un servicio de reconocimiento externo. Se solicita el micrófono solo al iniciar el dictado; no hay escucha en segundo plano ni grabación persistente. Esta versión no implementa transcripción offline ni carga de notas de voz al servidor.
