# Misión 04 — Remediación de seguridad y privacidad

## Alcance

Trabajo limitado a SSRF/DNS rebinding, olvido de memoria, exportación y borrado de datos, CORS, y separación del perfil personal de la identidad de Aranza. No incluye despliegue ni cambios de configuración de producción.

## Cambios realizados en el checkout

- lector_web.py: validar cada respuesta DNS y usar las direcciones validadas en el conector; desactivar caché DNS y redirects; restringir puertos a HTTP/80 y HTTPS/443; mantener TLS verificado y limitar tipo/tamaño de respuesta.
- main.py: borrar historial y decisiones de revisión al olvidar memoria; exportar perfil, conversaciones, memorias e investigaciones de la cuenta (incluidas fuentes, evidencia, relaciones e historial), sin exportar credenciales o sesiones; limpiar el perfil al borrar datos de cuenta; mantener el perfil acotado por account_id.
- CORS: permitir solo los métodos de API necesarios, con lista explícita de orígenes y sin credenciales cross-origin.
- Perfil: persistir preferencias personales por cuenta; mantener las instrucciones e identidad de Aranza como configuración de producto independiente. El perfil legado de owner se copia una sola vez mediante INSERT OR IGNORE; retirar su literal del código requiere una transición controlada para no perder el perfil ya persistido.
- Pruebas: cubrir rebinding y destinos no públicos, preflight CORS, aislamiento del perfil, exportación completa y eliminación de contenido privado.

## Validación ejecutada

- Pruebas enfocadas de Misión 04: 31 aprobadas.
- Suite completa local: 360 aprobadas en Windows con Python 3.15.1.
- compileall: aprobado para el árbol Python.
- CI de Python 3.11 en Ubuntu y Windows queda pendiente de la publicación del commit.
- Aviso no bloqueante: Starlette informa que la integración TestClient con httpx está deprecada y recomienda httpx2.
- Para el venv temporal se instalaron las dependencias de aplicación y pytest, omitiendo uvicorn[standard]: su instalación intentó compilar PyYAML sin Visual C++ Build Tools. La suite no importa ni ejecuta Uvicorn.
- Pruebas de red usan resolvers/respuestas simuladas, sin consultar destinos privados reales ni hacer llamadas a usuarios.


## Riesgos residuales y límites

- CORS controla qué navegadores pueden leer respuestas; no sustituye autenticación ni autorización.
- La biblioteca de investigaciones exporta el contenido que SQLite persiste. No hay persistencia de binarios de adjuntos en este alcance.
- La resolución validada reduce SSRF/DNS rebinding en el lector; la política de egreso de red del despliegue sigue siendo una defensa adicional.
- La identidad conversacional estática seguirá versionada como configuración del producto. El valor legado del perfil de owner permanece como semilla de compatibilidad en el código; deberá retirarse tras confirmar una migración persistida. El historial Git no se reescribe en esta misión.
- La auditoría arquitectónica existente se conserva sin cambios y describe el estado base anterior a esta remediación.

## Estado

Suite local y compileall aprobados; pendiente revisión final del diff y confirmación de CI Python 3.11 antes del cierre.
