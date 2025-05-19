"""bulk insert"""
import os
import pandas as pd
import pyodbc

def conectar_a_base_de_datos():
    """Conectar a la base de datos SQL Server."""
    SERVER = 'CHANG'
    DATABASE = 'MierdiInvestigacion'
    USERNAME = 'sa'
    PASSWORD = 'Once'
    conn_str = (
        f'DRIVER={{SQL Server}};SERVER={SERVER};'
        f'DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};'
        'TrustServerCertificate=yes'
    )
    return pyodbc.connect(conn_str)

def validar_y_convertir_datos(df):
    """Validar y convertir datos del DataFrame."""
    df['STATION'] = df['STATION'].astype(str)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['SOURCE'] = df['SOURCE'].astype(str)
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce').round(6)
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce').round(6)
    df['ELEVATION'] = pd.to_numeric(df['ELEVATION'], errors='coerce').round(2)
    for col in df.columns[df.columns.get_loc('NAME'):] :
        df[col] = df[col].fillna('').astype(str)
    return df

def agregar_columnas_faltantes(cursor, df):
    """Agregar columnas faltantes a la tabla en la base de datos."""
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'WeatherData'")
    columnas_existentes = [row.COLUMN_NAME for row in cursor.fetchall()]
    columnas_faltantes = [col for col in df.columns if col not in columnas_existentes]
    
    for columna in columnas_faltantes:
        if columna == 'DATE':
            cursor.execute(f"ALTER TABLE WeatherData ADD {columna} DATE")
        else:
            cursor.execute(f"ALTER TABLE WeatherData ADD {columna} NVARCHAR(MAX)")

def procesar_archivo_csv(cursor, ruta_completa):
    """Procesar un archivo CSV y realizar la inserción masiva en la base de datos."""
    print(f'Procesando archivo: {ruta_completa}')
    df = pd.read_csv(ruta_completa)
    df = validar_y_convertir_datos(df)
    
    # Agregar columnas faltantes
    agregar_columnas_faltantes(cursor, df)
    
    datos = [tuple(row) for row in df.to_numpy()]
    COLUMNAS = ', '.join(df.columns)
    PLACEHOLDERS = ', '.join(['?'] * len(df.columns))
    query = f"INSERT INTO WeatherData ({COLUMNAS}) VALUES ({PLACEHOLDERS})"
    
    # Realizar inserción masiva en bloques
    batch_size = 100_000
    for i in range(0, len(datos), batch_size):
        batch = datos[i:i + batch_size]
        cursor.executemany(query, batch)

def main():
    print('Iniciando inserción masiva...')
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()
    CARPETA_CSV = r'C:\Users\luisc\OneDrive - Instituto Tecnológico de Culiacán\Universidad\Semestre_8\Taller_Inv_II\ML\Data\py\Data'
    for archivo in os.listdir(CARPETA_CSV):
        if archivo.endswith('.csv'):
            ruta_completa = os.path.join(CARPETA_CSV, archivo)
            procesar_archivo_csv(cursor, ruta_completa)
            conn.commit()
    cursor.close()
    conn.close()
    print('Inserción completada.')

if __name__ == "__main__":
    main()
