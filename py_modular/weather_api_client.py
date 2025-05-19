"""
Cliente para la API de OpenWeatherMap que maneja las solicitudes de datos climáticos.
"""
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

class WeatherAPIClient:
    """
    Cliente para la API de OpenWeatherMap que gestiona las solicitudes 
    de datos climáticos actuales e históricos.
    """
    
    def __init__(self, api_key):
        """
        Inicializa el cliente de la API con la clave proporcionada.
        
        Args:
            api_key (str): La clave API de OpenWeatherMap.
        """
        self.api_key = api_key
        
    def obtener_datos_actuales(self, lat, lon):
        """
        Obtiene los datos climáticos actuales para una ubicación específica.
        
        Args:
            lat (float): Latitud de la ubicación.
            lon (float): Longitud de la ubicación.
            
        Returns:
            dict: Datos climáticos en formato JSON o None si hay un error.
        """
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al llamar a la API: {response.status_code} - {response.text}")
            return None
    
    def obtener_datos_historicos(self, lat, lon, dias=5):
        """
        Obtiene datos climáticos históricos para una ubicación específica.
        
        Args:
            lat (float): Latitud de la ubicación.
            lon (float): Longitud de la ubicación.
            dias (int): Número de días hacia atrás para obtener datos.
            
        Returns:
            pandas.DataFrame: DataFrame con datos históricos o None si hay un error.
        """
        fin = datetime.now()
        inicio = fin - timedelta(days=dias)

        start_unix = int(time.mktime(inicio.timetuple()))
        end_unix = int(time.mktime(fin.timetuple()))

        url = f"https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start_unix}&end={end_unix}&appid={self.api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "list" not in data:
                return None

            registros = []
            for item in data["list"]:
                timestamp = pd.to_datetime(item["dt"], unit='s')
                temp = item["main"]["temp"]
                humedad = item["main"]["humidity"]
                presion = item["main"]["pressure"]
                viento = item["wind"]["speed"]
                dew = self.calcular_punto_rocio(temp, humedad)
                
                # Calcular probabilidad de lluvia (simulada para demostración)
                # En una implementación real, esto podría usar un modelo de predicción
                probabilidad = min(100, max(0, (humedad - 40) + abs(30 - temp)))
                
                registros.append([timestamp, temp, humedad, dew, presion, viento, probabilidad])

            df = pd.DataFrame(registros, columns=["Fecha", "Temperatura", "Humedad", 
                                                "Punto_Rocio", "Presion", "Viento", 
                                                "Probabilidad_Lluvia"])
            return df.set_index("Fecha")
        else:
            print(f"Error API: {response.status_code}")
            return None
            
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
