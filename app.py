from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime
import os
import sys
import sqlite3
import json
from fpdf import FPDF
from PIL import Image
import io

# Función para obtener el directorio de recursos
def resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso"""
    return os.path.join(os.path.abspath("."), relative_path)

# Función para obtener la ruta de la base de datos
def get_database_path():
    """Obtiene la ruta de la base de datos"""
    return resource_path('informes.db')

app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
# Modificar las rutas para usar resource_path
app.config['UPLOAD_FOLDER'] = resource_path('static/uploads')
app.config['REPORT_FOLDER'] = resource_path('reports')
app.config['DATABASE'] = get_database_path()

# Crear directorios si no existen
for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORT_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Inicializar la base de datos
def init_db():
    """Inicializar la base de datos con las tablas necesarias"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        
        # Crear tabla de máquinas
        c.execute('''CREATE TABLE IF NOT EXISTS maquinas
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombre TEXT UNIQUE NOT NULL)''')
        
        # Crear tabla de informes
        c.execute('''CREATE TABLE IF NOT EXISTS informes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombre_maquina TEXT NOT NULL,
                      fecha DATE NOT NULL,
                      hora TIME NOT NULL,
                      descripcion TEXT NOT NULL,
                      imagen TEXT,
                      creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (nombre_maquina) REFERENCES maquinas (nombre))''')
        
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")

# Función auxiliar para parsear hora de manera segura
def parse_hora(hora_str):
    try:
        if hora_str and hora_str.strip():  # Si hay hora y no está vacía
            return datetime.strptime(hora_str, '%H:%M').time()
        else:  # Si no hay hora, usar medianoche
            return datetime.strptime('00:00', '%H:%M').time()
    except ValueError:
        # En caso de error, usar medianoche
        return datetime.strptime('00:00', '%H:%M').time()

# Función para redimensionar imagen manteniendo proporciones
def resize_image(image_path, max_width=150, max_height=150):
    try:
        with Image.open(image_path) as img:
            # Calcular nuevas dimensiones manteniendo proporciones
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return img
    except Exception:
        return None

# Obtener todas las máquinas
def get_maquinas():
    """Obtener todas las máquinas de la base de datos"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM maquinas ORDER BY nombre")
        maquinas = [{'id': row[0], 'nombre': row[1]} for row in c.fetchall()]
        conn.close()
        return maquinas
    except sqlite3.OperationalError as e:
        print(f"Error obteniendo máquinas: {e}")
        # Intentar crear las tablas si no existen
        crear_tablas_iniciales()
        # Intentar de nuevo
        try:
            conn = sqlite3.connect(app.config['DATABASE'])
            c = conn.cursor()
            c.execute("SELECT id, nombre FROM maquinas ORDER BY nombre")
            maquinas = [{'id': row[0], 'nombre': row[1]} for row in c.fetchall()]
            conn.close()
            return maquinas
        except:
            return []

# Agregar una máquina
def add_maquina(nombre):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    try:
        c.execute("INSERT INTO maquinas (nombre) VALUES (?)", (nombre,))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

# Eliminar una máquina y sus informes
def delete_maquina(nombre):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM informes WHERE nombre_maquina = ?", (nombre,))
    c.execute("DELETE FROM maquinas WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

# Obtener informes por máquina
def get_informes_por_maquina(nombre_maquina):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("""SELECT id, nombre_maquina, fecha, hora, descripcion, imagen, creado_en 
                 FROM informes 
                 WHERE nombre_maquina = ? 
                 ORDER BY fecha DESC, hora DESC""", (nombre_maquina,))
    informes = []
    for row in c.fetchall():
        informes.append({
            'id': row[0],
            'nombre_maquina': row[1],
            'fecha': datetime.strptime(row[2], '%Y-%m-%d').date(),
            'hora': parse_hora(row[3]),
            'descripcion': row[4],
            'imagen': row[5],
            'creado_en': datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')
        })
    conn.close()
    return informes

# Obtener todos los informes
def get_all_informes():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("""SELECT id, nombre_maquina, fecha, hora, descripcion, imagen, creado_en 
                 FROM informes 
                 ORDER BY nombre_maquina, fecha, hora""")
    informes = []
    for row in c.fetchall():
        informes.append({
            'id': row[0],
            'nombre_maquina': row[1],
            'fecha': datetime.strptime(row[2], '%Y-%m-%d').date(),
            'hora': parse_hora(row[3]),
            'descripcion': row[4],
            'imagen': row[5],
            'creado_en': datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')
        })
    conn.close()
    return informes

# Obtener informes por rango de fechas
def get_informes_por_fechas(fecha_inicio, fecha_fin):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("""SELECT id, nombre_maquina, fecha, hora, descripcion, imagen, creado_en 
                 FROM informes 
                 WHERE fecha BETWEEN ? AND ?
                 ORDER BY nombre_maquina, fecha, hora""", (fecha_inicio, fecha_fin))
    informes = []
    for row in c.fetchall():
        informes.append({
            'id': row[0],
            'nombre_maquina': row[1],
            'fecha': datetime.strptime(row[2], '%Y-%m-%d').date(),
            'hora': parse_hora(row[3]),
            'descripcion': row[4],
            'imagen': row[5],
            'creado_en': datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')
        })
    conn.close()
    return informes

# Agregar un informe
def add_informe(nombre_maquina, fecha, hora, descripcion, imagen):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("""INSERT INTO informes (nombre_maquina, fecha, hora, descripcion, imagen)
                 VALUES (?, ?, ?, ?, ?)""", 
              (nombre_maquina, fecha, hora, descripcion, imagen))
    conn.commit()
    informe_id = c.lastrowid
    conn.close()
    return informe_id

@app.route('/')
def index():
    maquinas = get_maquinas()
    return render_template('index.html', maquinas=maquinas)

@app.route('/maquina/<string:nombre_maquina>')
def ver_maquina(nombre_maquina):
    informes = get_informes_por_maquina(nombre_maquina)
    return render_template('maquina.html', nombre_maquina=nombre_maquina, informes=informes)

@app.route('/nueva_maquina', methods=['GET', 'POST'])
def nueva_maquina():
    if request.method == 'POST':
        nombre = request.form['nombre']
        
        if nombre:
            if add_maquina(nombre):
                flash('Máquina agregada correctamente')
                return redirect(url_for('index'))
            else:
                flash('Ya existe una máquina con ese nombre')
        else:
            flash('Por favor ingrese el nombre de la máquina')
    
    return render_template('nueva_maquina.html')

@app.route('/nuevo_informe', methods=['GET', 'POST'])
def nuevo_informe():
    if request.method == 'POST':
        nombre_maquina = request.form['nombre_maquina']
        fecha = request.form['fecha']
        hora = request.form['hora']
        descripcion = request.form['descripcion']
        
        if nombre_maquina and fecha and hora and descripcion:
            # Guardar imagen si se proporciona
            imagen_nombre = None
            if 'imagen' in request.files:
                imagen = request.files['imagen']
                if imagen.filename != '':
                    # Generar nombre único para la imagen
                    extension = imagen.filename.rsplit('.', 1)[1].lower() if imagen.filename else ''
                    imagen_nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nombre_maquina}.{extension}"
                    imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen_nombre))
            
            # Crear el informe
            add_informe(nombre_maquina, fecha, hora, descripcion, imagen_nombre)
            flash('Informe agregado correctamente')
            return redirect(url_for('ver_maquina', nombre_maquina=nombre_maquina))
        else:
            flash('Por favor complete todos los campos obligatorios')
    
    maquinas = get_maquinas()
    return render_template('nuevo_informe.html', maquinas=maquinas, datetime=datetime)

@app.route('/generar_informe_pdf')
def generar_informe_pdf():
    # Obtener todos los informes
    informes = get_all_informes()
    
    # Crear el PDF con diseño profesional
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Configurar fuentes y colores profesionales
    pdf.set_fill_color(25, 118, 210)  # Azul corporativo
    pdf.set_text_color(255, 255, 255)  # Blanco
    pdf.set_draw_color(25, 118, 210)  # Azul corporativo
    
    # Encabezado profesional con logo (simulado)
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'INFORME TÉCNICO DE MÁQUINAS', 0, 1, 'C', True)
    pdf.ln(2)
    
    # Línea divisoria
    pdf.set_draw_color(255, 255, 255)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Subtítulo con fechas en caja destacada
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(255, 255, 255)
    
    # Obtener el rango de fechas de los informes
    if informes:
        fechas = [i['fecha'] for i in informes]
        fecha_inicio = min(fechas).strftime('%d/%m/%Y')
        fecha_fin = max(fechas).strftime('%d/%m/%Y')
        periodo_text = f'PERIODO: {fecha_inicio} AL {fecha_fin}'
    else:
        periodo_text = 'PERIODO: [Sin informes registrados]'
    
    pdf.cell(0, 12, periodo_text, 1, 1, 'C', True)
    pdf.ln(8)
    
    # Información del técnico con diseño de tabla
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(45, 10, 'Técnico Responsable:', 1, 0, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Willian Ruiz Z', 1, 1, 'L')
    pdf.ln(5)
    
    # Agrupar informes por máquina
    informes_por_maquina = {}
    for informe in informes:
        if informe['nombre_maquina'] not in informes_por_maquina:
            informes_por_maquina[informe['nombre_maquina']] = []
        informes_por_maquina[informe['nombre_maquina']].append(informe)
    
    # Ordenar las máquinas alfabéticamente
    maquinas_ordenadas = sorted(informes_por_maquina.keys())
    
    # Contenido por máquina con diseño mejorado
    for nombre_maquina in maquinas_ordenadas:
        # Verificar si hay espacio suficiente para la sección
        if pdf.get_y() > 240:
            pdf.add_page()
        
        # Título de la máquina con estilo profesional
        pdf.set_fill_color(33, 150, 243)  # Azul más claro
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 12, nombre_maquina, 1, 1, 'L', True)
        pdf.ln(5)
        
        # Resetear colores para contenido
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        
        # Informes de la máquina
        informes_maquina = informes_por_maquina[nombre_maquina]
        # Ordenar por fecha y hora
        informes_maquina.sort(key=lambda x: (x['fecha'], x['hora']))
        
        for informe in informes_maquina:
            # Formatear la fecha y hora
            fecha_str = informe['fecha'].strftime('%d/%m/%Y')
            hora_str = informe['hora'].strftime('%H:%M') if informe['hora'].strftime('%H:%M') != '00:00' else ''
            
            # Crear entrada del informe con mejor organización
            pdf.set_font('Arial', 'B', 11)
            
            # Línea de fecha y hora
            linea_fecha = f"Fecha: {fecha_str}"
            if hora_str:
                linea_fecha += f" | Hora: {hora_str}"
            
            pdf.write(6, linea_fecha)
            pdf.ln(6)
            
            # Descripción
            pdf.set_font('Arial', '', 11)
            pdf.write(6, informe['descripcion'].encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(8)
            
            # Agregar imagen si existe (centrada y con espacio)
            if informe['imagen']:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], informe['imagen'])
                if os.path.exists(image_path):
                    try:
                        # Verificar espacio suficiente
                        if pdf.get_y() + 50 > pdf.h - pdf.b_margin:
                            pdf.add_page()
                            pdf.ln(5)
                        
                        # Centrar la imagen
                        pdf.cell(0, 10, '', 0, 1, 'C')
                        pdf.image(image_path, w=45, h=45)
                        pdf.ln(5)
                    except Exception as e:
                        pass  # Si hay error con la imagen, continuar sin mostrarla
            
            # Línea divisoria sutil entre informes
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(5)
        
        pdf.ln(3)
    
    # Pie de página profesional
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f'Informe generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}', 0, 0, 'C')
    
    # Guardar el PDF
    filename = f"informe_maquinas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(app.config['REPORT_FOLDER'], filename)
    pdf.output(filepath)
    
    # Enviar el archivo para descarga
    return send_file(filepath, as_attachment=True)

@app.route('/generar_informe_personalizado', methods=['POST'])
def generar_informe_personalizado():
    titulo = request.form['titulo']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    
    # Obtener informes por rango de fechas
    informes = get_informes_por_fechas(fecha_inicio, fecha_fin)
    
    # Crear el PDF con diseño profesional
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Configurar fuentes y colores profesionales
    pdf.set_fill_color(25, 118, 210)  # Azul corporativo
    pdf.set_text_color(255, 255, 255)  # Blanco
    pdf.set_draw_color(25, 118, 210)  # Azul corporativo
    
    # Encabezado profesional
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, titulo, 0, 1, 'C', True)
    pdf.ln(2)
    
    # Línea divisoria
    pdf.set_draw_color(255, 255, 255)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Subtítulo con fechas en caja destacada
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(255, 255, 255)
    fecha_inicio_fmt = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
    fecha_fin_fmt = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d/%m/%Y')
    periodo_text = f'PERIODO: {fecha_inicio_fmt} AL {fecha_fin_fmt}'
    
    pdf.cell(0, 12, periodo_text, 1, 1, 'C', True)
    pdf.ln(8)
    
    # Información del técnico con diseño de tabla
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(45, 10, 'Técnico Responsable:', 1, 0, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Willian Ruiz Z', 1, 1, 'L')
    pdf.ln(5)
    
    # Agrupar informes por máquina
    informes_por_maquina = {}
    for informe in informes:
        if informe['nombre_maquina'] not in informes_por_maquina:
            informes_por_maquina[informe['nombre_maquina']] = []
        informes_por_maquina[informe['nombre_maquina']].append(informe)
    
    # Ordenar las máquinas alfabéticamente
    maquinas_ordenadas = sorted(informes_por_maquina.keys())
    
    # Contenido por máquina con diseño mejorado
    for nombre_maquina in maquinas_ordenadas:
        # Verificar si hay espacio suficiente para la sección
        if pdf.get_y() > 240:
            pdf.add_page()
        
        # Título de la máquina con estilo profesional
        pdf.set_fill_color(33, 150, 243)  # Azul más claro
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 12, nombre_maquina, 1, 1, 'L', True)
        pdf.ln(5)
        
        # Resetear colores para contenido
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        
        # Informes de la máquina
        informes_maquina = informes_por_maquina[nombre_maquina]
        # Ordenar por fecha y hora
        informes_maquina.sort(key=lambda x: (x['fecha'], x['hora']))
        
        for informe in informes_maquina:
            # Formatear la fecha y hora
            fecha_str = informe['fecha'].strftime('%d/%m/%Y')
            hora_str = informe['hora'].strftime('%H:%M') if informe['hora'].strftime('%H:%M') != '00:00' else ''
            
            # Crear entrada del informe con mejor organización
            pdf.set_font('Arial', 'B', 11)
            
            # Línea de fecha y hora
            linea_fecha = f"Fecha: {fecha_str}"
            if hora_str:
                linea_fecha += f" | Hora: {hora_str}"
            
            pdf.write(6, linea_fecha)
            pdf.ln(6)
            
            # Descripción
            pdf.set_font('Arial', '', 11)
            pdf.write(6, informe['descripcion'].encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(8)
            
            # Agregar imagen si existe (centrada y con espacio)
            if informe['imagen']:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], informe['imagen'])
                if os.path.exists(image_path):
                    try:
                        # Verificar espacio suficiente
                        if pdf.get_y() + 50 > pdf.h - pdf.b_margin:
                            pdf.add_page()
                            pdf.ln(5)
                        
                        # Centrar la imagen
                        pdf.cell(0, 10, '', 0, 1, 'C')
                        pdf.image(image_path, w=45, h=45)
                        pdf.ln(5)
                    except Exception as e:
                        pass  # Si hay error con la imagen, continuar sin mostrarla
            
            # Línea divisoria sutil entre informes
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(5)
        
        pdf.ln(3)
    
    # Pie de página profesional
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f'Informe generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}', 0, 0, 'C')
    
    # Guardar el PDF
    filename = f"informe_personalizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(app.config['REPORT_FOLDER'], filename)
    pdf.output(filepath)
    
    # Enviar el archivo para descarga
    return send_file(filepath, as_attachment=True)

@app.route('/eliminar_maquina/<string:nombre_maquina>', methods=['POST'])
def eliminar_maquina(nombre_maquina):
    delete_maquina(nombre_maquina)
    flash('Máquina eliminada correctamente')
    return redirect(url_for('index'))

def crear_tablas_iniciales():
    """Crear tablas iniciales si no existen"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        
        # Crear tabla de máquinas
        c.execute('''CREATE TABLE IF NOT EXISTS maquinas
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombre TEXT UNIQUE NOT NULL)''')
        
        # Crear tabla de informes
        c.execute('''CREATE TABLE IF NOT EXISTS informes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombre_maquina TEXT NOT NULL,
                      fecha DATE NOT NULL,
                      hora TIME NOT NULL,
                      descripcion TEXT NOT NULL,
                      imagen TEXT,
                      creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (nombre_maquina) REFERENCES maquinas (nombre))''')
        
        conn.commit()
        conn.close()
        print("Tablas creadas correctamente")
        return True
    except Exception as e:
        print(f"Error creando tablas: {e}")
        return False

# Inicializar la base de datos
init_db()
# Asegurarse de que las tablas existen
crear_tablas_iniciales()

if __name__ == '__main__':
    app.run(debug=True)