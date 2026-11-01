# Aranza v1.94 — Biblioteca persistente de investigaciones

- Añade tabla SQLite `investigaciones`, con índices por cuenta, fecha y conversación.
- Añade endpoints autenticados para guardar, listar, consultar y eliminar expedientes.
- Cada expediente conserva consulta, título, resumen, hasta 30 fuentes filtradas y matriz de evidencia estructurada.
- Aislamiento estricto por `account_id`; una cuenta no puede consultar ni borrar expedientes de otra.
- La eliminación de datos personales de la cuenta incluye ahora sus investigaciones guardadas.
- Los expedientes no se guardan automáticamente: requieren una acción explícita del cliente mediante `POST /research/library`.
- No incluye todavía una interfaz visual de biblioteca ni exportación de informes.
