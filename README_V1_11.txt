ARANZA v1.11 - MEMORIA EXPLÍCITA DESDE EL CHAT

NOVEDADES
- Escribe "Recuerda que prefiero respuestas directas" para guardar un recuerdo desde el chat.
- También reconoce "Quiero que recuerdes que...", "Guarda en memoria que..." y "Anota que...".
- Aranza confirma cuando guarda un recuerdo nuevo.
- Puedes revisar y borrar recuerdos desde el panel «Memoria de Aranza».
- Los recuerdos idénticos no se duplican en la misma cuenta.
- No guarda mediante esta función contraseñas, claves API, tokens de acceso ni secretos similares.
- Los mensajes normales no se convierten en recuerdos permanentes por defecto.

INSTALACIÓN
1. Conserva las versiones anteriores.
2. Antes de sustituir archivos, haz copia de seguridad de la base de datos SQLite y del archivo .env.
3. Descomprime el parche y sustituye los archivos incluidos; no reemplaces la base de datos ni .env.
4. Prueba primero con una copia del entorno real.
5. Ejecuta: python -m pytest -q

VALIDACIÓN LOCAL
- 31 pruebas aprobadas.
- Las pruebas de chat usan una respuesta simulada y no consumen llamadas de API.

LÍMITES
- No está desplegada en producción.
- Sigue siendo una instancia de una sola cuenta.
- La memoria automática general aún no está implementada: en esta versión se guarda solo cuando se pide expresamente.
