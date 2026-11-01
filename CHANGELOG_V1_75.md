# Aranza v1.75

## Análisis visual opcional

- La interfaz admite adjuntar JPG, JPEG, PNG y WEBP además de documentos existentes.
- Nuevo endpoint autenticado `POST /tools/analyze-image`.
- Validación de tamaño máximo (5 MB), extensión, MIME declarado y firma básica del archivo.
- Procesamiento en memoria; no se guarda la imagen ni se registra su contenido.
- Proveedor de visión separado mediante `ARANZA_VISION_PROVIDER`, `ARANZA_VISION_BASE_URL`, `ARANZA_VISION_API_KEY`, `ARANZA_VISION_MODEL` y `ARANZA_VISION_TIMEOUT_SECONDS`.
- Si no existe proveedor multimodal configurado, devuelve HTTP 503 con una explicación y no intenta usar el modelo de texto.
- Prompt de análisis limita afirmaciones a lo visible, pide expresar incertidumbre e ignora instrucciones incrustadas.

## Compatibilidad y límites

- No cambia los endpoints conversacionales existentes.
- No se incluye una clave de proveedor ni se habilita visión automáticamente.
- La función requiere un modelo compatible con mensajes multimodales en formato OpenAI Chat Completions.
- La imagen se transmite al proveedor externo configurado al solicitar el análisis; revisa sus condiciones de privacidad.
- El análisis visual no conserva la imagen en el historial persistente.

## Verificación

- 231 pruebas aprobadas.
- `python -m py_compile main.py modelos.py` correcto.
