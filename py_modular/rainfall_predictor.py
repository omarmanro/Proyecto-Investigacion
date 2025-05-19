"""
Predictor de lluvia que utiliza un modelo LSTM para hacer predicciones.
"""
import numpy as np
import tensorflow as tf
import joblib

class RainfallPredictor:
    """
    Clase para cargar y utilizar un modelo de predicción de lluvia basado en LSTM.
    """
    
    def __init__(self, modelo_path, scaler_path):
        """
        Inicializa el predictor cargando el modelo y el scaler desde archivos.
        
        Args:
            modelo_path (str): Ruta al archivo del modelo guardado.
            scaler_path (str): Ruta al archivo del scaler guardado.
        """
        self.modelo = self._cargar_modelo(modelo_path)
        self.scaler = self._cargar_scaler(scaler_path)
        
    def _cargar_modelo(self, modelo_path):
        """
        Carga un modelo de TensorFlow desde un archivo.
        
        Args:
            modelo_path (str): Ruta al archivo del modelo.
            
        Returns:
            tf.keras.Model: El modelo cargado.
        """
        try:
            return tf.keras.models.load_model(modelo_path)
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            return None
    
    def _cargar_scaler(self, scaler_path):
        """
        Carga un scaler de scikit-learn desde un archivo.
        
        Args:
            scaler_path (str): Ruta al archivo del scaler.
            
        Returns:
            scaler: El scaler cargado.
        """
        try:
            return joblib.load(scaler_path)
        except Exception as e:
            print(f"Error al cargar el scaler: {e}")
            return None
    
    def predecir(self, datos_escalados):
        """
        Hace una predicción de probabilidad de lluvia usando el modelo LSTM.
        
        Args:
            datos_escalados (numpy.ndarray): Datos ya escalados y formateados para el modelo.
            
        Returns:
            float: Probabilidad de lluvia (0-1).
        """
        if self.modelo is None:
            print("No se ha cargado ningún modelo")
            return 0.0
            
        # Hacer la predicción
        try:
            prediccion = self.modelo.predict(datos_escalados)
            return prediccion[0][0]  # Extraer el valor escalar
        except Exception as e:
            print(f"Error al realizar la predicción: {e}")
            return 0.0
