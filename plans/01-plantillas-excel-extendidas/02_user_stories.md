# Historias de Usuario: Plantillas de Excel Extendidas

## HU 0: Diseño de Arquitectura y Creación de Plantillas

- **Status**: `Completed`
- **DOR**:
    - [x] Claridad: El equipo entiende el objetivo.
    - [x] Completitud: La información funcional y técnica está definida.
    - [x] Criterios de Aceptación: Definidos.
    - [x] Dependencias: Identificadas.
    - [x] Aprobación del PO: Aprobado.

- **Información Funcional**:
    - **Gherkin**: `Como` desarrollador, `quiero` definir la arquitectura para manejar múltiples versiones de plantillas y crear los archivos físicos de Excel, `para` asegurar que la implementación esté bien planificada y los activos estén listos.

- **Información Técnica**:
    - **Especificaciones**:
        - El `ExcelProcessor` deberá ser modificado para detectar la versión de la plantilla (simple o completa) basándose en la presencia de columnas específicas.
        - Se debe planificar la ubicación de los archivos de plantilla (ej. en un directorio `/templates`).
        - Se deben crear dos archivos `.xlsx`: `plantilla_simple.xlsx` y `plantilla_completa.xlsx`.
    - **Diagramas C4**: No se requieren para esta fase inicial.

- **Tareas**:
    - `[x]` Tarea 0.1 (Dev): Diseñar la estrategia en `utils/excel_processor.py` para la detección dinámica de plantillas.
    - `[x]` Tarea 0.2 (Dev): Crear el archivo `templates/plantilla_simple.xlsx` con las columnas actuales.
    - `[x]` Tarea 0.3 (Dev): Crear el archivo `templates/plantilla_completa.xlsx` incluyendo columnas para campos opcionales como `taxes`, `due`, etc.
    - `[x]` Tarea 0.4 (Dev): Actualizar `docs/API.md` para documentar la estructura del nuevo payload completo.
    - `[x]` Tarea 0.5 (QA/Dev): Actualizar la documentación del proyecto afectada por esta HU.

---

## HU 1: Implementar Lógica de Procesamiento para Plantilla Completa

- **Status**: `In Progress`
- **DOR**:
    - [x] Claridad: El equipo entiende el objetivo.
    - [x] Completitud: La información funcional y técnica está definida.
    - [x] Criterios de Aceptación: Definidos.
    - [x] Dependencias: Identificadas.
    - [x] Aprobación del PO: Aprobado.

- **Información Funcional**:
    - **Gherkin**: `Como` contador, `quiero` subir un archivo de Excel usando la "plantilla completa", `para` poder crear comprobantes contables con información detallada como impuestos y fechas de vencimiento.

- **Información Técnica**:
    - **Especificaciones**:
        - Modificar `utils/excel_processor.py` para leer las nuevas columnas de la plantilla completa.
        - La lógica debe ser capaz de construir el payload JSON anidado que la API de Siigo espera (ej. el array `taxes`).
        - El sistema debe seguir funcionando correctamente si se sube una plantilla simple.

- **Tareas**:
    - `[x]` Tarea 1.1 (Dev): Implementar la lógica en `utils/excel_processor.py` para detectar la plantilla completa.
    - `[x]` Tarea 1.2 (Dev): Implementar el formateo del payload extendido, incluyendo los nuevos campos.
    - `[/]` Tarea 1.3 (Dev): Crear un nuevo archivo de prueba `tests/test_full_template_processor.py`.
    - `[ ]` Tarea 1.4 (QA): Validar que tanto la plantilla simple como la completa se procesan correctamente.
    - `[ ]` Tarea 1.5 (QA/Dev): Actualizar la documentación del proyecto afectada por esta HU.

---

## HU 2: Implementar Descarga de Plantillas en la Interfaz

- **Status**: `In Progress`
- **DOR**:
    - [x] Claridad: El equipo entiende el objetivo.
    - [x] Completitud: La información funcional y técnica está definida.
    - [x] Criterios de Aceptación: Definidos.
    - [x] Dependencias: Identificadas.
    - [x] Aprobación del PO: Aprobado.

- **Información Funcional**:
    - **Gherkin**: `Como` usuario, `quiero` poder descargar la plantilla de Excel correcta (simple o completa) directamente desde la aplicación, `para` poder preparar mis datos fácilmente y sin errores.

- **Información Técnica**:
    - **Especificaciones**:
        - Utilizar el componente `st.download_button` de Streamlit.
        - Los archivos de plantilla deben estar almacenados en el repositorio, por ejemplo, en `/templates`.

- **Tareas**:
    - `[x]` Tarea 2.1 (Dev): Añadir una nueva sección en la UI de `main.py` para la descarga de plantillas.
    - `[x]` Tarea 2.2 (Dev): Implementar un botón de descarga para `plantilla_simple.xlsx`.
    - `[x]` Tarea 2.3 (Dev): Implementar un botón de descarga para `plantilla_completa.xlsx`.
    - `[ ]` Tarea 2.4 (QA): Verificar que los botones descargan los archivos correctos.
    - `[ ]` Tarea 2.5 (QA/Dev): Actualizar la documentación del proyecto afectada por esta HU.
