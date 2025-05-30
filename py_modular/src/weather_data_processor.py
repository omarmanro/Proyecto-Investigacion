"""
Procesador de datos meteorológicos que prepara los datos para la predicción.
"""
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from config import config

class WeatherDataProcessor:
    """
    Clase para procesar y transformar datos meteorológicos,
    preparándolos para su visualización y uso en modelos predictivos.
    """
    
    def __init__(self, scaler):
        """
        Inicializa el procesador con un scaler para normalizar los datos.
        
        Args:
            scaler: Un objeto scaler de scikit-learn para normalización de datos.
        """
        self.scaler = scaler
        
    def procesar_datos_actuales(self, datos_climaticos, lat, lon):
        """
        Procesa datos climáticos actuales desde la API y los prepara para la predicción.
        
        Args:
            datos_climaticos (dict): Datos JSON de la API de OpenWeatherMap.
            lat (float): Latitud de la ubicación.
            lon (float): Longitud de la ubicación.
            
        Returns:
            dict: Un diccionario con los datos procesados.
            numpy.ndarray: Datos normalizados y formateados para el modelo LSTM.
        """
        if not datos_climaticos or "main" not in datos_climaticos:
            return None, None
            
        # Extraer valores relevantes
        temp = datos_climaticos['main']['temp']
        humedad = datos_climaticos['main']['humidity']
        dew = self.calcular_punto_rocio(temp, humedad)
        elevation = 4.87  # Estimado, se podría obtener de una API de elevación
        wnd_direction = datos_climaticos.get('wind', {}).get('deg', 0)
        wnd_speed = datos_climaticos.get('wind', {}).get('speed', 0)
        cig_height = 22000  # No disponible en OpenWeatherMap
        vis_distance = datos_climaticos.get('visibility', 10000)
        slp = datos_climaticos['main']['pressure']
        date = pd.Timestamp.now().timestamp()
        
        # Crear diccionario para facilitar el acceso a los datos
        datos_procesados = {
            'timestamp': date,
            'lat': lat,
            'lon': lon,
            'elevation': elevation,
            'wind_direction': wnd_direction,
            'wind_speed': wnd_speed,
            'ceiling_height': cig_height,
            'visibility': vis_distance,
            'temperature': temp,
            'dew_point': dew,
            'pressure': slp,
            'humidity': humedad
        }
        
        # Preparar array para el modelo
        input_data = np.array([[
            date, lat, lon, elevation, 
            wnd_direction, wnd_speed, cig_height, vis_distance,
            temp, dew, slp
        ]])
        
        # Aplicar normalización
        input_scaled = self.scaler.transform(input_data)
        
        # Reformatear para LSTM (1 muestra, 1 paso de tiempo, n características)
        input_lstm = np.reshape(input_scaled, (1, 1, input_scaled.shape[1]))
        
        return datos_procesados, input_lstm
        
    @staticmethod
    def calcular_punto_rocio(temperatura, humedad_relativa):
        """
        Calcula el punto de rocío basado en la temperatura y humedad.
        
        Args:
            temperatura (float): Temperatura en grados Celsius.
            humedad_relativa (float): Humedad relativa en porcentaje.
            
        Returns:
            float: Punto de rocío calculado en grados Celsius.
        """
        return temperatura - ((100 - humedad_relativa) / 5)
        
    def generar_datos_ejemplo(self, datos_reales, n_muestras=30):
        """
        Genera datos históricos simulados basados en datos reales actuales.
        Útil para demostración cuando no hay datos históricos disponibles.
        
        Args:
            datos_reales (dict): Datos meteorológicos reales actuales.
            n_muestras (int): Número de muestras a generar.
            
        Returns:
            pandas.DataFrame: DataFrame con datos históricos simulados.
        """
        # Generar fechas históricas
        fechas = pd.date_range(end=pd.Timestamp.now(), periods=n_muestras, freq='D')
        
        # Usar generador de números aleatorios moderno
        rng = np.random.default_rng(42)
        
        # Generar valores que siguen patrones realistas basados en los datos actuales
        temp = datos_reales.get('temperature', 25)
        temp_hist = np.sin(np.linspace(0, 6, n_muestras)) * 5 + temp + rng.normal(0, 2, n_muestras)
        
        humedad_hist = np.sin(np.linspace(0, 6, n_muestras)) * 10 + 70 + rng.normal(0, 5, n_muestras)
        humedad_hist = np.clip(humedad_hist, 0, 100)
        
        dew_hist = [self.calcular_punto_rocio(t, h) for t, h in zip(temp_hist, humedad_hist)]
        
        presion_hist = np.ones(n_muestras) * datos_reales.get('pressure', 1010) + rng.normal(0, 1, n_muestras)
        
        viento_hist = np.abs(np.sin(np.linspace(0, 6, n_muestras))) * 10 + rng.normal(0, 1, n_muestras)
        viento_hist = np.clip(viento_hist, 0, 20)
        
        # Probabilidad de lluvia simulada
        rain_prob_hist = np.abs(np.sin(np.linspace(0, 6, n_muestras))) * 0.5 + 0.2 + rng.normal(0, 0.1, n_muestras)
        rain_prob_hist = np.clip(rain_prob_hist, 0, 1) * 100
        
        # Crear DataFrame
        df_hist = pd.DataFrame({
            'Fecha': fechas,
            'Temperatura': temp_hist,
            'Humedad': humedad_hist,
            'Punto_Rocio': dew_hist,
            'Presion': presion_hist,
            'Viento': viento_hist,
            'Probabilidad_Lluvia': rain_prob_hist
        })
        
        return df_hist.set_index('Fecha')
    
    def obtener_datos_historicos_bd(self, lat, lon, limit=10_000):
        """
        Obtiene datos históricos desde la base de datos SQL Server para una ubicación específica.
        
        Args:
            lat (float): Latitud de la ubicación.
            lon (float): Longitud de la ubicación.
            limit (int): Número máximo de registros a obtener.
            
        Returns:
            pandas.DataFrame: DataFrame con datos históricos, o None si hay un error.
        """
        try:
            # Crear conexión a la base de datos usando configuración
            engine = create_engine(config.get_mssql_connection_string())
            
            # Consulta para obtener datos históricos cercanos a la ubicación
            # Usamos una tolerancia para encontrar datos cercanos a las coordenadas
            query = f"""
                SELECT TOP {limit}
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
                    ABS(LATITUDE - {lat}) < 0.3 AND
                    ABS(LONGITUDE - ({lon})) < 0.3
                ORDER BY DATE DESC
            """
            
            # Ejecutar consulta usando pandas con la API actualizada
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            
            if df.empty:
                return None
                
            # Convertir la columna de fecha a datetime
            df['Fecha'] = pd.to_datetime(df['DATE'])
            df = df.drop(columns=['DATE'])
            
            # Multiplicar por 100 para convertir a porcentaje si la columna es binaria
            if 'Probabilidad_Lluvia' in df.columns:
                df['Probabilidad_Lluvia'] = df['Probabilidad_Lluvia'] * 100
                
            # Establecer la fecha como índice
            df = df.set_index('Fecha')
            
            return df
        except Exception as e:
            print(f"Error al obtener datos históricos de la BD: {e}")
            return None
