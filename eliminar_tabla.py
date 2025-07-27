import sqlite3
import os

# Verificar que existe la base de datos
if os.path.exists('db.sqlite3'):
    # Conectar a la base de datos
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Ver tablas existentes antes
    print("Tablas antes de eliminar:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    for tabla in tablas:
        print(f"  - {tabla[0]}")
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comunidad_registrohorario;")
    tabla_existe = cursor.fetchone()
    
    if tabla_existe:
        # Eliminar la tabla
        cursor.execute("DROP TABLE comunidad_registrohorario;")
        conn.commit()
        print("\n✅ Tabla 'comunidad_registrohorario eliminada exitosamente")
        
        # Mostrar tablas después
        print("\nTablas después de eliminar:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        for tabla in tablas:
            print(f"  - {tabla[0]}")
    else:
        print("❌ La tabla 'comunidad_registrohorario no existe")
    
    # Cerrar conexión
    conn.close()
else:
    print("❌ El archivo db.sqlite3 no existe en este directorio")