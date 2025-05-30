"""bulk insert usando Supabase API"""
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
import os
from pathlib import Path
# Cargar .env desde el directorio raíz del proyecto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

def conectar_a_supabase():
    """Conectar a Supabase usando la API oficial."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar definidos en el archivo .env")
    
    return create_client(url, key)

def validar_y_convertir_datos(df):
    """Validar y convertir datos del DataFrame."""
    df['STATION'] = df['STATION'].astype(str)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['SOURCE'] = df['SOURCE'].astype(str)
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce').round(6)
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce').round(6)
    df['ELEVATION'] = pd.to_numeric(df['ELEVATION'], errors='coerce').round(2)
    for col in df.columns[df.columns.get_loc('NAME'):]:
        df[col] = df[col].fillna('').astype(str)
    return df

def procesar_archivo_csv(supabase, ruta_completa):
    """Procesar un archivo CSV y realizar la inserción en Supabase."""
    print(f'Procesando archivo: {ruta_completa}')
    df = pd.read_csv(ruta_completa)
    df = validar_y_convertir_datos(df)
    
    # Convertir DataFrame a formato de registros para Supabase
    registros = df.to_dict(orient='records')
    
    # Insertar datos en bloques de 1000 registros (límite recomendado para Supabase)
    batch_size = 1000
    for i in range(0, len(registros), batch_size):
        batch = registros[i:i + batch_size]
        # Usar upsert para evitar duplicados (basado en la clave primaria)
        result = supabase.table('WeatherData').upsert(batch).execute()
        print(f'Procesado lote {i//batch_size + 1}/{(len(registros)//batch_size) + 1}')
        
        # Verificar errores
        if hasattr(result, 'error') and result.error:
            print(f"Error al insertar datos: {result.error}")

def main():
    print('Iniciando inserción masiva en Supabase...')
    
    try:
        # Conectar a Supabase
        supabase = conectar_a_supabase()
        
        # Procesar archivos CSV
        CARPETA_CSV = r'/py_ai-Chang/Data'
        for archivo in os.listdir(CARPETA_CSV):
            if archivo.endswith('.csv'):
                ruta_completa = os.path.join(CARPETA_CSV, archivo)
                procesar_archivo_csv(supabase, ruta_completa)
                
        print('Inserción completada con éxito.')
        
    except Exception as e:
        print(f'Error durante la inserción: {str(e)}')

if __name__ == "__main__":
    main()
