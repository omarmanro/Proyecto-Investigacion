"""
Paquete principal de la aplicación de predicción de lluvia.
Contiene todos los módulos core de la aplicación.
"""

__version__ = "1.0.0"
__author__ = "Luis Chang"
__description__ = "Aplicación modular de predicción de lluvia usando ML y datos meteorológicos"

# Exportar las clases principales para facilitar su importación
from .weather_api_client import WeatherAPIClient
from .weather_data_processor import WeatherDataProcessor
from .rainfall_predictor import RainfallPredictor
from .weather_visualizer import WeatherVisualizer
from .config import Config

# Crear una instancia de la configuración para uso global
config = Config()
