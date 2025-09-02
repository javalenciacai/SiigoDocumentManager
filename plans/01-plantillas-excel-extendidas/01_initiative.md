# Iniciativa: Plantillas de Excel Extendidas y Descargables

- **Status**: `Pending`

## Problema

El sistema actual solo procesa un conjunto básico de campos para los comprobantes contables, lo que limita su utilidad para escenarios que requieren más detalle (ej. impuestos, retenciones, fechas de vencimiento). Además, los usuarios no tienen una forma fácil de obtener la plantilla de Excel correcta, lo que puede llevar a errores de formato.

## Solución

Vamos a ampliar el sistema para que sea compatible con dos versiones de plantillas de Excel:

1.  **Plantilla Simple**: La versión actual, para casos de uso rápidos y sencillos.
2.  **Plantilla Completa**: Una nueva versión que incluye todos los campos disponibles en el endpoint de Comprobantes Contables de la API de Siigo.

El sistema deberá detectar automáticamente qué plantilla se está utilizando y procesarla correctamente. Adicionalmente, implementaremos una sección en la interfaz de usuario para que los usuarios puedan descargar cualquiera de las dos plantillas directamente.

## Alcance (Scope)

- **Dentro del alcance**:
    - Modificar el `ExcelProcessor` para que identifique y procese ambas plantillas.
    - Crear los dos archivos de plantilla (`.xlsx`).
    - Añadir botones de descarga en la interfaz de Streamlit.
    - Actualizar la documentación interna para reflejar el nuevo payload completo.

- **Fuera del alcance (Rabbit Holes)**:
    - Esta iniciativa **solo** aplica a **Comprobantes Contables**. No se añadirá soporte para otros documentos como Facturas o Notas de Crédito.
    - No se implementará una interfaz de gestión de plantillas. La solución se limitará a dos botones de descarga.
    - Solo se incluirán los campos estándar de la API de Siigo. No se añadirán campos personalizados.
