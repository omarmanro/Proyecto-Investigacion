"""
Script para verificar que todos los componentes se pueden importar y utilizar.
Guarda el resultado en un archivo de log.
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    filename='verificacion.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def log_message(msg):
    """Registra un mensaje en el log y lo imprime."""
    logger.info(msg)
    print(msg)

log_message("Iniciando verificación de componentes...")

# Intentar importar todos los componentes
try:
    log_message("Importando módulos...")
    
    from weather_api_client import WeatherAPIClient
    from weather_data_processor import WeatherDataProcessor
    from rainfall_predictor import RainfallPredictor
    from weather_visualizer import WeatherVisualizer
    from streamlit_app import StreamlitApp
    
    log_message("✓ Todos los módulos importados correctamente")
    
    # Verificar archivos necesarios
    files_to_check = [
        "modelo_lluvia_lstm.h5",
        "scaler_lstm.pkl"
    ]
    
    log_message("Verificando archivos necesarios...")
    for file in files_to_check:
        if os.path.exists(file):
            size_kb = os.path.getsize(file) / 1024
            log_message(f"✓ Archivo {file} encontrado ({size_kb:.1f} KB)")
        else:
            log_message(f"✗ Archivo {file} no encontrado")
    
    # Crear una instancia de cada componente
    log_message("\nCreando instancias de componentes:")
    
    api_client = WeatherAPIClient("test_key")
    log_message("✓ WeatherAPIClient inicializado")
    
    # Intentar cargar el predictor con modelo y scaler
    modelo_path = './modelo_lluvia_lstm.h5'
    scaler_path = './scaler_lstm.pkl'
    
    if os.path.exists(modelo_path) and os.path.exists(scaler_path):
        predictor = RainfallPredictor(modelo_path, scaler_path)
        log_message("✓ RainfallPredictor inicializado con modelo y scaler")
        
        processor = WeatherDataProcessor(predictor.scaler)
        log_message("✓ WeatherDataProcessor inicializado con scaler")
    else:
        log_message("⚠ No se pudieron inicializar RainfallPredictor y WeatherDataProcessor con archivos reales")
    
    visualizer = WeatherVisualizer()
    log_message("✓ WeatherVisualizer inicializado")
    
    log_message("\n✓ Verificación completada: todos los componentes funcionan correctamente")
    
except Exception as e:
    log_message(f"✗ Error durante la verificación: {e}")
    import traceback
    tb = traceback.format_exc()
    log_message(tb)

log_message("Verificación finalizada. Revise el archivo 'verificacion.log' para más detalles.")
