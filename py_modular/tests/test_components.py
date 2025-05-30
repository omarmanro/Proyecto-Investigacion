"""
Script para pruebas unitarias de los componentes modulares de la aplicación de predicción de lluvia.
"""
import os
import sys
import unittest
import pandas as pd
import numpy as np

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar módulos de la aplicación desde el paquete src
try:
    from src.weather_api_client import WeatherAPIClient
    from src.weather_data_processor import WeatherDataProcessor
    from src.rainfall_predictor import RainfallPredictor
    from src.weather_visualizer import WeatherVisualizer
    from src.config import Config
    
    # Crear instancia de configuración
    config = Config()
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    sys.exit(1)

class TestWeatherAPIClient(unittest.TestCase):
    """Pruebas para el cliente de API del clima."""
    def setUp(self):
        # API key desde configuración
        self.api_key = config.OPENWEATHER_API_KEY
        self.client = WeatherAPIClient(self.api_key)
        
        # Coordenadas de prueba desde configuración
        self.lat = config.DEFAULT_LATITUDE
        self.lon = config.DEFAULT_LONGITUDE
        
    def test_obtener_datos_actuales(self):
        """Prueba la obtención de datos climáticos actuales."""
        print("Probando obtener_datos_actuales...")
        
        datos = self.client.obtener_datos_actuales(self.lat, self.lon)
        
        # Verificar que se obtuvieron datos
        self.assertIsNotNone(datos)
        print("✓ Datos recibidos")
        
        # Verificar campos clave
        self.assertIn('main', datos)
        self.assertIn('wind', datos)
        self.assertIn('weather', datos)
        print("✓ Estructura de datos correcta")
        
        # Mostrar datos de ejemplo
        print(f"Temperatura: {datos['main']['temp']}°C")
        print(f"Humedad: {datos['main']['humidity']}%")
        print(f"Condición: {datos['weather'][0]['main']}")
        
        return datos
    
    def test_obtener_datos_historicos(self):
        """Prueba la obtención de datos históricos."""
        print("Probando obtener_datos_historicos...")
        
        # Intentar obtener datos históricos (puede fallar debido a límites de API)
        try:
            df_hist = self.client.obtener_datos_historicos(self.lat, self.lon, dias=3)
            
            if df_hist is not None:
                # Verificar que se obtuvo un dataframe
                self.assertIsInstance(df_hist, pd.DataFrame)
                print("✓ DataFrame recibido")
                
                # Verificar columnas clave
                for columna in ['Temperatura', 'Humedad', 'Presion']:
                    self.assertIn(columna, df_hist.columns)
                print("✓ Columnas correctas en el DataFrame")
                  # Mostrar primeras filas
                print("\nPrimeras filas de datos históricos:")
                print(df_hist.head())
            else:
                print("⚠ No se pudieron obtener datos históricos (posiblemente por límites de API)")
        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"⚠ Error en obtener_datos_historicos: {e}")


class TestWeatherDataProcessor(unittest.TestCase):
    """Pruebas para el procesador de datos meteorológicos."""
    
    def setUp(self):
        # Usar rutas desde la configuración
        try:
            self.predictor = RainfallPredictor(config.MODEL_PATH, config.SCALER_PATH)
            self.processor = WeatherDataProcessor(self.predictor.scaler)
        except (OSError, ImportError) as e:
            print(f"⚠ No se pudo cargar el scaler: {e}")
            self.processor = WeatherDataProcessor(None)
        
        # Datos de prueba
        self.test_data = {
            'main': {
                'temp': 28.5,
                'humidity': 75,
                'pressure': 1012
            },
            'wind': {
                'speed': 3.2,
                'deg': 180
            },
            'weather': [{'id': 800, 'main': 'Clear'}],
            'coord': {'lat': 24.8087, 'lon': -107.3940}
        }
        
    def test_procesar_datos_actuales(self):
        """Prueba el procesamiento de datos actuales."""
        print("Probando procesar_datos_actuales...")
        
        datos_procesados, input_lstm = self.processor.procesar_datos_actuales(
            self.test_data,
            self.test_data['coord']['lat'],
            self.test_data['coord']['lon']
        )
        
        # Verificar datos procesados
        self.assertIsInstance(datos_procesados, dict)
        print("✓ Datos procesados correctamente")
        
        # Verificar campos clave
        for campo in ['temperature', 'humidity', 'pressure', 'dew_point', 'wind_speed']:
            self.assertIn(campo, datos_procesados)
        print("✓ Todos los campos requeridos están presentes")
        
        # Verificar formato de entrada LSTM
        self.assertIsInstance(input_lstm, np.ndarray)
        print(f"✓ Input LSTM creado con forma {input_lstm.shape}")
        
        # Mostrar datos procesados
        print("\nDatos procesados:")
        for k, v in datos_procesados.items():
            print(f"  {k}: {v}")
            
        return datos_procesados, input_lstm
    
    def test_generar_datos_ejemplo(self):
        """Prueba la generación de datos de ejemplo."""
        print("Probando generar_datos_ejemplo...")
        
        datos_base = {
            'temperature': 28.5,
            'humidity': 75,
            'pressure': 1012,
            'dew_point': 22.3,
            'wind_speed': 3.2,
            'wind_direction': 180
        }
        
        df = self.processor.generar_datos_ejemplo(datos_base)
        
        # Verificar que se generó un dataframe
        self.assertIsInstance(df, pd.DataFrame)
        print("✓ DataFrame generado correctamente")
        
        # Verificar columnas y longitud
        self.assertGreater(len(df), 0)
        print(f"✓ DataFrame contiene {len(df)} filas")
        
        # Mostrar primeras filas
        print("\nPrimeras filas de datos generados:")
        print(df.head())
        
        return df


class TestRainfallPredictor(unittest.TestCase):
    """Pruebas para el predictor de lluvia."""
    
    def setUp(self):
        # Usar rutas desde la configuración
        self.predictor = RainfallPredictor(config.MODEL_PATH, config.SCALER_PATH)
        
    def test_cargar_modelo(self):
        """Prueba la carga del modelo."""
        print("Probando carga del modelo...")
        
        # Verificar que el modelo se cargó correctamente
        self.assertIsNotNone(self.predictor.modelo)
        print("✓ Modelo cargado correctamente")
          # Verificar que el scaler se cargó correctamente
        self.assertIsNotNone(self.predictor.scaler)
        print("✓ Scaler cargado correctamente")
        
    def test_predecir(self):
        """Prueba la predicción con el modelo."""
        print("Probando predecir...")
          # Crear datos de prueba aleatorios para predicción (5 características)
        rng = np.random.default_rng(42)  # Seed fijo para reproducibilidad
        sample_data = rng.random((1, 1, 5))
        
        # Realizar predicción
        prob = self.predictor.predecir(sample_data)
        
        # Verificar resultado
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        print(f"✓ Predicción realizada: {prob:.4f}")


class TestWeatherVisualizer(unittest.TestCase):
    """Pruebas para el visualizador de datos meteorológicos."""
    
    def setUp(self):
        self.visualizer = WeatherVisualizer()
        
        # Datos de prueba
        self.valores = [25, 70, 19, 4, 1013/10]
        self.variables = ['Temperatura', 'Humedad', 'Punto de Rocío', 'Velocidad del Viento', 'Presión']
        self.valores_ref = [22, 80, 18, 5, 101]
        
    def test_plot_radar_chart(self):
        """Prueba la generación de gráfico de radar."""
        print("Probando plot_radar_chart...")
        
        # Crear gráfico
        fig = self.visualizer.plot_radar_chart(self.valores, self.variables, self.valores_ref)
        
        # Verificar que se generó una figura
        self.assertIsNotNone(fig)
        print("✓ Gráfico de radar generado")
        
    def test_plot_bar_chart(self):
        """Prueba la generación de gráfico de barras."""
        print("Probando plot_bar_chart...")
        
        # Crear gráfico
        variables_barras = self.variables[:4]
        valores_barras = self.valores[:4]
        colores = ['#72B7B2', '#DA8137', '#54A24B', '#4C78A8']
        
        fig = self.visualizer.plot_bar_chart(valores_barras, variables_barras, colores)
        
        # Verificar que se generó una figura
        self.assertIsNotNone(fig)
        print("✓ Gráfico de barras generado")
        
    def test_plot_gauge(self):
        """Prueba la generación de indicador tipo gauge."""
        print("Probando plot_gauge...")
        
        # Crear gráfico
        fig = self.visualizer.plot_gauge(75, "Probabilidad de lluvia (%)")
        
        # Verificar que se generó una figura
        self.assertIsNotNone(fig)
        print("✓ Indicador gauge generado")
        
    def test_plot_heatmap(self):
        """Prueba la generación de mapa de calor."""
        print("Probando plot_heatmap...")
        
        # Crear datos para el mapa de calor
        variables_calor = {
            'Temperatura': 28.5,
            'Humedad': 75,
            'Punto de Rocío': 22.3,
            'Velocidad del Viento': 3.2,
            'Presión': 1012
        }
        
        # Crear gráfico
        fig = self.visualizer.plot_heatmap(variables_calor)
        
        # Verificar que se generó una figura
        self.assertIsNotNone(fig)
        print("✓ Mapa de calor generado")


def run_tests():
    """Ejecuta todas las pruebas unitarias."""
    print("="*80)
    print(" "*30 + "PRUEBAS UNITARIAS")
    print("="*80)
    
    # 1. Pruebas de WeatherAPIClient
    print("\n1. Pruebas de WeatherAPIClient")
    print("-"*50)
    api_suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherAPIClient)
    unittest.TextTestRunner(verbosity=0).run(api_suite)
    
    # 2. Pruebas de WeatherDataProcessor
    print("\n2. Pruebas de WeatherDataProcessor")
    print("-"*50)
    processor_suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherDataProcessor)
    unittest.TextTestRunner(verbosity=0).run(processor_suite)
    
    # 3. Pruebas de RainfallPredictor
    print("\n3. Pruebas de RainfallPredictor")
    print("-"*50)
    predictor_suite = unittest.TestLoader().loadTestsFromTestCase(TestRainfallPredictor)
    unittest.TextTestRunner(verbosity=0).run(predictor_suite)
    
    # 4. Pruebas de WeatherVisualizer
    print("\n4. Pruebas de WeatherVisualizer")
    print("-"*50)
    visualizer_suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherVisualizer)
    unittest.TextTestRunner(verbosity=0).run(visualizer_suite)
    
    print("\n" + "="*80)
    print("Pruebas completadas.")
    print("="*80)


if __name__ == "__main__":
    run_tests()
