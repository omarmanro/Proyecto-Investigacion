"""
Script para probar la conexión a la base de datos
y verificar la recuperación de datos históricos.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from config import config

def probar_conexion_bd():
    """
    Prueba la conexión a la base de datos SQL Server.
    
    Returns:
        bool: True si la conexión es exitosa, False si hay un error.
    """    
    try:
        # Crear conexión a la base de datos usando configuración
        engine = create_engine(config.get_db_connection_string())
        
        # Intentar ejecutar una consulta simple usando la API actualizada de SQLAlchemy
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM WeatherData")).scalar()
        
        print(f"Conexión exitosa. Total de registros en WeatherData: {result}")
        return True
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return False

def obtener_datos_muestra(lat=None, lon=None, limit=10):
    """
    Obtiene una muestra de datos históricos para una ubicación específica.
    
    Args:
        lat (float): Latitud de la ubicación.
        lon (float): Longitud de la ubicación.
        limit (int): Número máximo de registros a obtener.
        
    Returns:
        pandas.DataFrame: DataFrame con datos históricos, o None si hay un error.
    """
    # Usar valores por defecto de configuración si no se proporcionan
    if lat is None:
        lat = config.DEFAULT_LATITUDE
    if lon is None:
        lon = config.DEFAULT_LONGITUDE
        
    try:
        # Crear conexión a la base de datos usando configuración
        engine = create_engine(config.get_db_connection_string())
        
        # Consulta para obtener datos históricos cercanos a la ubicación
        query = f"""
            SELECT TOP {limit} 
                STATION,
                DATE, 
                LATITUDE, 
                LONGITUDE, 
                TMP as Temperatura, 
                DEW as Punto_Rocio, 
                WND_SPEED as Viento, 
                SLP as Presion,
                LLOVIÓ as Probabilidad_Lluvia
            FROM WeatherData
            WHERE 
                ABS(LATITUDE - {lat}) < 0.1 AND
                ABS(LONGITUDE - ({lon})) < 0.1
            ORDER BY DATE DESC
        """
        
        # Ejecutar consulta usando pandas
        df = pd.read_sql_query(text(query), engine.connect())
        
        if df.empty:
            print("No se encontraron datos para la ubicación especificada.")
            return None
            
        print(f"Datos obtenidos para la ubicación (lat={lat}, lon={lon}):")
        print(df.head())
        return df
        
    except Exception as e:
        print(f"Error al obtener datos históricos: {e}")
        return None

if __name__ == "__main__":
    # Probar conexión a la base de datos
    if probar_conexion_bd():
        # Si la conexión es exitosa, obtener datos de muestra
        obtener_datos_muestra()