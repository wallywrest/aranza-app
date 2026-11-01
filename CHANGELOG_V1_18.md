# Aranza v1.18

## Fuentes web más limpias y trazables
- Normaliza URLs de resultados y desenvuelve enlaces de redirección de DuckDuckGo cuando contienen el destino original.
- Elimina fragmentos y parámetros de seguimiento comunes para reducir duplicados y enlaces ruidosos.
- Incluye el dominio como metadato explícito en resultados y en las fuentes mostradas en el chat.
- Rechaza destinos locales/no públicos, esquemas no HTTP(S) y URLs con credenciales incrustadas.
- Mantiene la advertencia de que los fragmentos de búsqueda no equivalen a verificar el contenido completo de una página.

## Validación
- 53 pruebas automatizadas locales aprobadas.
- `main.py` y `busqueda_web.py` compilan correctamente.
- JavaScript de la interfaz comprobado sintácticamente.

## Límites conocidos
- No descarga ni verifica el contenido completo de las páginas; los resultados siguen basándose en títulos y fragmentos del buscador.
- No se desplegó en un servidor ni se probaron llamadas reales al proveedor de búsqueda en esta validación.
