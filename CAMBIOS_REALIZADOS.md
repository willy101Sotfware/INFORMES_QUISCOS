# Cambios Realizados en el Sistema de Informes

## Resumen
Se implementaron dos mejoras principales al sistema:

### 1. ✅ Ordenamiento de Informes por Máquina y Fecha (Ascendente)

**Cambios realizados:**
- Los informes ahora se ordenan automáticamente por:
  1. Nombre de máquina (alfabéticamente)
  2. Fecha (ascendente - de más antigua a más reciente)
  3. Hora (ascendente)

**Archivos modificados:**
- `app.py` - Funciones actualizadas:
  - `get_all_informes()` - línea 160: `ORDER BY nombre_maquina, fecha, hora`
  - `get_informes_por_fechas()` - línea 183: `ORDER BY nombre_maquina, fecha, hora`
  - `generar_informe_pdf()` - línea 412: Ordenamiento de informes por fecha y hora
  - `generar_informe_personalizado()` - línea 568: Ordenamiento de informes por fecha y hora

**Resultado:**
- Los PDFs generados muestran las máquinas en orden alfabético
- Dentro de cada máquina, los informes aparecen ordenados por fecha y hora de forma ascendente
- Los informes guardados en la base de datos mantienen este orden

### 2. ✅ Soporte para Segunda Imagen de Evidencia

**Cambios realizados:**

#### Base de Datos:
- Se agregó la columna `imagen2` a la tabla `informes`
- Migración automática para bases de datos existentes
- Script de migración manual disponible: `migrate_db.py`

#### Backend (`app.py`):
- `add_informe()` - Ahora acepta y guarda `imagen2`
- `update_informe()` - Actualiza ambas imágenes
- `get_informes_por_maquina()` - Incluye `imagen2` en los resultados
- `get_all_informes()` - Incluye `imagen2` en los resultados
- `get_informes_por_fechas()` - Incluye `imagen2` en los resultados
- `get_informe_by_id()` - Incluye `imagen2` en los resultados
- Rutas `/nuevo_informe` y `/editar_informe` - Manejan la carga de ambas imágenes

#### Frontend:
- **nuevo_informe.html**: 
  - Campo "Imagen de Evidencia 1"
  - Campo "Imagen de Evidencia 2"
  
- **editar_informe.html**:
  - Campos para actualizar ambas imágenes
  - Muestra las imágenes actuales antes de editar
  
- **maquina.html**:
  - Muestra ambas imágenes lado a lado
  - Mismo tamaño para ambas imágenes (max-height: 300px)
  - Diseño responsive con columnas

#### PDF:
- Ambas imágenes se incluyen en el PDF
- Mismo tamaño: 45x45 unidades
- Mismo estilo y centrado
- Se muestran una debajo de la otra en el informe

## Características Técnicas

### Ordenamiento:
```sql
ORDER BY nombre_maquina, fecha, hora
```

### Imágenes:
- **Formato**: JPG, PNG, GIF
- **Tamaño máximo**: 5MB
- **Nombres de archivo**: 
  - Imagen 1: `YYYYMMDD_HHMMSS_NombreMaquina.ext`
  - Imagen 2: `YYYYMMDD_HHMMSS_NombreMaquina_2.ext`

### Migración Automática:
- Al iniciar la aplicación, se verifica si existe la columna `imagen2`
- Si no existe, se agrega automáticamente
- No se pierden datos existentes

## Instrucciones de Uso

### Para agregar un nuevo informe con dos imágenes:
1. Ir a "Nuevo Informe"
2. Llenar los campos obligatorios
3. Seleccionar "Imagen de Evidencia 1" (opcional)
4. Seleccionar "Imagen de Evidencia 2" (opcional)
5. Guardar

### Para generar PDF ordenado:
1. Hacer clic en "Generar Informe PDF"
2. El PDF se descargará automáticamente con:
   - Máquinas en orden alfabético
   - Informes por fecha ascendente
   - Ambas imágenes incluidas

### Migración manual (si es necesario):
```bash
python migrate_db.py
```

## Archivos Modificados

1. **app.py** - Backend principal
2. **templates/nuevo_informe.html** - Formulario de nuevo informe
3. **templates/editar_informe.html** - Formulario de edición
4. **templates/maquina.html** - Vista de informes por máquina

## Archivos Nuevos

1. **migrate_db.py** - Script de migración manual
2. **CAMBIOS_REALIZADOS.md** - Este documento

## Compatibilidad

- ✅ Compatible con bases de datos existentes
- ✅ Los informes antiguos sin segunda imagen funcionan normalmente
- ✅ No se requiere reinstalación
- ✅ Migración automática al iniciar la aplicación

## Notas Importantes

- Las imágenes son opcionales, se puede crear un informe sin imágenes
- Se puede agregar solo una imagen o ambas
- En el PDF, ambas imágenes tienen el mismo tamaño (45x45)
- En la vista web, las imágenes se muestran lado a lado con max-height de 300px
- El ordenamiento es automático y no requiere configuración adicional
