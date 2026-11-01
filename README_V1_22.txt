PROYECTO ARANZA v1.22

CAMBIO PRINCIPAL
La búsqueda y la lectura de fuentes web ahora pasan por el endpoint autenticado /tools/research. La interfaz hace una sola solicitud de investigación, recibe hasta cinco resultados y el backend intenta leer como máximo dos páginas. Si una lectura falla, conserva el fragmento del buscador y continúa.

VALIDACIÓN LOCAL
65 pruebas automatizadas aprobadas. Sintaxis Python y JavaScript comprobada. No equivale a validación en producción ni a pruebas reales de todos los proveedores externos.

INSTALACIÓN
Esta entrega es un parche de desarrollo. No sobrescribas la base de datos SQLite ni el archivo .env. Antes de instalar en un servidor, haz copia de seguridad, revisa la configuración y valida la migración con una copia de los datos. El parche no se ha desplegado en tu hosting.
