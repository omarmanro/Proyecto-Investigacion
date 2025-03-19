import os
import pandas as pd
import pyodbc

def conectar_a_base_de_datos():
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

def extraer_valores_wnd(wnd):
    try:
        partes = wnd.split(',')
        direccion = float(partes[0]) if partes[0].isdigit() else None
        velocidad = float(partes[3]) / 10 if partes[3].isdigit() else None  # Convertir de 0051 a 5.1
        return direccion, velocidad
    except:
        return None, None

def extraer_valores_cig(cig):
    try:
        partes = cig.split(',')
        altura = float(partes[0]) if partes[0].isdigit() else None
        return altura
    except:
        return None

def extraer_valores_vis(vis):
    try:
        partes = vis.split(',')
        visibilidad = float(partes[0]) if partes[0].isdigit() else None
        return visibilidad
    except:
        return None

def validar_y_convertir_datos(df):
    df.columns = df.columns.str.strip()
    df['STATION'] = df['STATION'].astype(str)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S.%f')
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce').round(6)
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce').round(6)
    df['ELEVATION'] = pd.to_numeric(df['ELEVATION'], errors='coerce').round(2)
    
    # Procesar columnas WND, CIG y VIS
    df['WND_DIRECTION'], df['WND_SPEED'] = zip(*df['WND'].map(extraer_valores_wnd))
    df['CIG_HEIGHT'] = df['CIG'].map(extraer_valores_cig)
    df['VIS_DISTANCE'] = df['VIS'].map(extraer_valores_vis)
    
    df['TMP'] = pd.to_numeric(df['TMP'], errors='coerce')
    df['DEW'] = pd.to_numeric(df['DEW'], errors='coerce')
    df['SLP'] = pd.to_numeric(df['SLP'], errors='coerce')
    df['LLOVIÓ'] = df['LLOVIÓ'].apply(lambda x: 1 if str(x).strip() == '1' else 0)
    return df

def crear_tabla(cursor):
    cursor.execute("""
    IF OBJECT_ID('WeatherData', 'U') IS NOT NULL
        DROP TABLE WeatherData;
    CREATE TABLE WeatherData (
        STATION NVARCHAR(50),
        DATE DATETIME,
        LATITUDE FLOAT,
        LONGITUDE FLOAT,
        ELEVATION FLOAT,
        WND_DIRECTION FLOAT,
        WND_SPEED FLOAT,
        CIG_HEIGHT FLOAT,
        VIS_DISTANCE FLOAT,
        TMP FLOAT,
        DEW FLOAT,
        SLP FLOAT,
        LLOVIÓ BIT
    )
    """)

def procesar_archivo_csv(cursor, ruta_completa):
    print(f'Procesando archivo: {ruta_completa}')
    df = pd.read_csv(ruta_completa)
    df = validar_y_convertir_datos(df)
    
    columnas_a_insertar = ['STATION', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION',
                           'WND_DIRECTION', 'WND_SPEED', 'CIG_HEIGHT', 'VIS_DISTANCE',
                           'TMP', 'DEW', 'SLP', 'LLOVIÓ']
    datos = [tuple(row) for row in df[columnas_a_insertar].to_numpy()]
    COLUMNAS = ', '.join(columnas_a_insertar)
    PLACEHOLDERS = ', '.join(['?'] * len(columnas_a_insertar))
    query = f"INSERT INTO WeatherData ({COLUMNAS}) VALUES ({PLACEHOLDERS})"
    
    batch_size = 100_000
    for i in range(0, len(datos), batch_size):
        batch = datos[i:i + batch_size]
        cursor.executemany(query, batch)

def main():
    print('Iniciando inserción masiva...')
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()
    
    crear_tabla(cursor)
    
    CARPETA_CSV = r'C:\Users\luisc\OneDrive - Instituto Tecnológico de Culiacán\Universidad\Semestre_8\Taller_Inv_II\ML\Data\Proyecto-Investigacion\Datos\DatosLimpios'
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
