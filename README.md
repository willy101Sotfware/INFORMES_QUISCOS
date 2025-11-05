# Informes de Máquinas

Sistema de gestión de informes para máquinas con registro de novedades, fechas, horas y evidencias visuales.

## Características

- Registro de máquinas con nombre (almacenamiento persistente en base de datos SQLite)
- Creación de informes quincenales con:
  - Nombre de la máquina
  - Fecha y hora de la novedad
  - Descripción detallada de la novedad
  - **Hasta 2 imágenes de evidencia** (todas se muestran con el mismo tamaño)
- **Ordenamiento automático** de informes por máquina y fecha (ascendente)
- Generación de informe consolidado en PDF con diseño profesional
- **Reseteo quincenal**: Botón para limpiar todos los informes manteniendo las máquinas
- Interfaz limpia y organizada tipo dashboard
- Vista de informes por máquina ordenados cronológicamente
- Edición de informes existentes con actualización de imágenes

## Requisitos

- Python 3.7 o superior
- Pip (gestor de paquetes de Python)

## Instalación

1. Clonar o descargar el repositorio
2. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución como aplicación web

1. Ejecutar la aplicación:
   ```bash
   python app.py
   ```
2. Abrir el navegador en `http://localhost:5000`

## Convertir en aplicación de escritorio

### Opción 1: Usar el script de instalación (recomendado)
```bash
python instalar_app.py
```

### Opción 2: Crear ejecutable manualmente
1. Instalar PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Crear el ejecutable:
   ```bash
   pyinstaller --onefile --windowed app.py
   ```
3. El ejecutable se creará en la carpeta `dist`

### Opción 3: Usar los archivos batch (Windows)
1. Ejecutar `CrearEjecutable.bat` para crear el ejecutable
2. Ejecutar `IniciarInformes.bat` para iniciar la aplicación

## Uso

1. **Agregar nuevas máquinas** desde la página principal
2. **Crear informes** para cada máquina con:
   - Nombre de la máquina (seleccionado de la lista)
   - Fecha (se establece automáticamente al día actual)
   - Hora (se establece automáticamente a la hora actual)
   - Descripción detallada de la novedad
   - **Imagen de evidencia 1** (opcional)
   - **Imagen de evidencia 2** (opcional)
3. **Visualizar informes** organizados por máquina y fecha (orden ascendente)
4. **Editar informes** existentes y actualizar imágenes
5. **Generar informe PDF**:
   - Hacer clic en "Generar Informe PDF" en la página principal
   - El PDF incluye todas las máquinas ordenadas alfabéticamente
   - Los informes dentro de cada máquina están ordenados por fecha ascendente
   - Ambas imágenes se incluyen con el mismo tamaño
6. **Resetear informes cada 15 días**:
   - Hacer clic en "Resetear Todos los Informes" (botón rojo)
   - Confirmar dos veces la acción
   - Se eliminan todos los informes e imágenes
   - Las máquinas se mantienen para el siguiente período

## Estructura del Proyecto

- `app.py`: Aplicación principal Flask
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, imágenes)
- `static/uploads/`: Directorio para imágenes de evidencia
- `reports/`: Directorio para informes PDF generados
- `informes.db`: Base de datos SQLite para almacenamiento persistente
- `requirements.txt`: Dependencias del proyecto
- `instalar_app.py`: Script para crear aplicación de escritorio
- `iniciar_app.py`: Script para iniciar la aplicación
- `*.bat`: Archivos batch para Windows

## Tecnologías Utilizadas

- Python
- Flask (framework web)
- SQLite (base de datos)
- FPDF2 (generación de PDFs)
- Bootstrap 5 (interfaz responsive)
- HTML5 y CSS3