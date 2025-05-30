"""
Script para migrar datos de SQL Server local a Supabase.
Este script:
1. Se conecta a la base de datos SQL Server local
2. Consulta los datos de la tabla WeatherData
3. Se conecta a Supabase
4. Crea la tabla en Supabase si no existe
5. Transfiere los datos por lotes
"""
import os
import pandas as pd
import pyodbc
import psycopg2
from dotenv import load_dotenv
import time
from tqdm import tqdm

# Obtener la ruta del directorio actual del script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Cargar variables de entorno desde el archivo .env en el directorio principal del proyecto
dotenv_path = os.path.abspath(os.path.join(script_dir, '..', '.env'))
load_dotenv(dotenv_path)

# Configuración
BATCH_SIZE = 1000  # Cantidad de registros a insertar por lote

def conectar_a_sql_server():
    """Conectar a la base de datos SQL Server local."""
    print("Conectando a SQL Server...")
    SERVER = os.getenv('MSSQL_SERVER', 'CHANG')
    DATABASE = os.getenv('MSSQL_DATABASE', 'MierdiInvestigacion')
    USERNAME = os.getenv('MSSQL_USERNAME', 'sa')
    PASSWORD = os.getenv('MSSQL_PASSWORD', 'Once')
    DRIVER = os.getenv('MSSQL_DRIVER', 'ODBC+Driver+17+for+SQL+Server')
    # Reemplazar los + del driver por espacios para el formato de pyodbc
    DRIVER = DRIVER.replace('+', ' ')
    TRUST_CERT = os.getenv('MSSQL_TRUST_CERTIFICATE', 'yes')
    TIMEOUT = os.getenv('MSSQL_TIMEOUT', '30')
    
    # Formato de conexión para pyodbc
    conn_str = (
        f'DRIVER={{{DRIVER}}};SERVER={SERVER};'
        f'DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};'
        f'TrustServerCertificate={TRUST_CERT};'
        f'timeout={TIMEOUT};'
    )
    
    # También imprimir la URL de SQLAlchemy para referencia
    sqlalchemy_url = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate={TRUST_CERT}&timeout={TIMEOUT}'
    print(f"SQLAlchemy URL: {sqlalchemy_url}")
    print(f"pyodbc conn_str: {conn_str}")
    
    return pyodbc.connect(conn_str)

def conectar_a_supabase_postgres():
    """Conectar a la base de datos PostgreSQL de Supabase."""
    print("Conectando a Supabase PostgreSQL...")
    
    # Usando la cadena de conexión proporcionada para Supabase
    # postgresql://postgres:[YOUR-PASSWORD]@db.ppnipjvymkovbadqjoze.supabase.co:5432/postgres
    USERNAME = 'postgres'
    PASSWORD = os.getenv('SUPABASE_PASSWORD', 'Once')  # Usar contraseña de variable de entorno o valor por defecto
    SERVER = 'db.ppnipjvymkovbadqjoze.supabase.co'
    PORT = '5432'
    DATABASE = 'postgres'  # Base de datos por defecto en Supabase
    
    # Formato de conexión para psycopg2
    conn_str = (
        f"host={SERVER} dbname={DATABASE} user={USERNAME} "
        f"password={PASSWORD} port={PORT}"
    )
    
    # También imprimir la URL formato URI para referencia
    uri_conn_str = f"postgresql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"
    print(f"PostgreSQL URI: {uri_conn_str}")
    print(f"PostgreSQL conn_str: {conn_str}")
    
    return psycopg2.connect(conn_str)

def crear_tabla_en_supabase(cursor):
    """Crear la tabla WeatherData en Supabase si no existe."""
    print("Creando tabla WeatherData en Supabase si no existe...")
    
    # Leer y ejecutar el script SQL
    script_path = os.path.join('migraciones', 'create_weatherdata_table.sql')
    with open(script_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()
    
    # Ejecutar script SQL
    cursor.execute(sql_script)

def obtener_total_registros(cursor):
    """Obtener el número total de registros en la tabla WeatherData."""
    cursor.execute("SELECT COUNT(*) FROM WeatherData")
    return cursor.fetchone()[0]

def migrar_datos():
    """Migrar datos de SQL Server a Supabase."""
    try:
        # Conectar a SQL Server
        sql_conn = conectar_a_sql_server()
        sql_cursor = sql_conn.cursor()
        
        # Obtener el número total de registros
        total_registros = obtener_total_registros(sql_cursor)
        print(f"Total de registros a migrar: {total_registros:,}")
        
        # Conectar a Supabase PostgreSQL
        pg_conn = conectar_a_supabase_postgres()
        pg_cursor = pg_conn.cursor()
        
        # Crear tabla en Supabase
        crear_tabla_en_supabase(pg_cursor)
        pg_conn.commit()
        
        # Preparar consulta para obtener datos en lotes
        offset = 0
        registros_procesados = 0
        
        # Preparar consulta para inserción en PostgreSQL
        insert_query = """
        INSERT INTO "WeatherData" (
            "STATION", "DATE", "LATITUDE", "LONGITUDE", "ELEVATION", 
            "WND_DIRECTION", "WND_SPEED", "CIG_HEIGHT", "VIS_DISTANCE", 
            "TMP", "DEW", "SLP", "LLOVIÓ"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ("STATION", "DATE") DO NOTHING
        """
        
        # Iniciar barra de progreso
        progress_bar = tqdm(total=total_registros, desc="Migrando datos")
        
        # Migrar datos en lotes
        while offset < total_registros:
            # Consultar lote de datos de SQL Server
            select_query = f"""
            SELECT STATION, DATE, LATITUDE, LONGITUDE, ELEVATION, 
                   WND_DIRECTION, WND_SPEED, CIG_HEIGHT, VIS_DISTANCE, 
                   TMP, DEW, SLP, LLOVIÓ
            FROM WeatherData
            ORDER BY DATE
            OFFSET {offset} ROWS
            FETCH NEXT {BATCH_SIZE} ROWS ONLY
            """
            sql_cursor.execute(select_query)
            
            # Obtener datos
            batch_data = sql_cursor.fetchall()
            
            # Convertir a lista de tuplas para inserción
            datos = [tuple(row) for row in batch_data]
            
            # Insertar datos en Supabase
            pg_cursor.executemany(insert_query, datos)
            pg_conn.commit()
            
            # Actualizar contadores
            registros_en_lote = len(batch_data)
            offset += registros_en_lote
            registros_procesados += registros_en_lote
            
            # Actualizar barra de progreso
            progress_bar.update(registros_en_lote)
            
            # Breve pausa para no sobrecargar la base de datos
            time.sleep(0.1)
        
        # Cerrar barra de progreso
        progress_bar.close()
        
        print(f"\n✅ Migración completada: {registros_procesados:,} registros transferidos")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
    
    finally:
        # Cerrar conexiones
        if 'sql_conn' in locals():
            sql_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando migración de SQL Server a Supabase...")
    migrar_datos()
