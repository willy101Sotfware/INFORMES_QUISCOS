"""
Script de migración para agregar la columna imagen2 a la base de datos existente
"""
import sqlite3
import os

def migrate_database():
    """Agregar columna imagen2 a la tabla informes si no existe"""
    db_path = 'informes.db'
    
    if not os.path.exists(db_path):
        print("No se encontró la base de datos. No es necesario migrar.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar si la columna imagen2 ya existe
        c.execute("PRAGMA table_info(informes)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'imagen2' not in columns:
            print("Agregando columna imagen2 a la tabla informes...")
            c.execute("ALTER TABLE informes ADD COLUMN imagen2 TEXT")
            conn.commit()
            print("✓ Migración completada exitosamente")
        else:
            print("✓ La columna imagen2 ya existe. No es necesario migrar.")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error durante la migración: {e}")

if __name__ == '__main__':
    migrate_database()
