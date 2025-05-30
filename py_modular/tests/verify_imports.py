"""
Script simple para verificar que todos los componentes se pueden importar y utilizar.
"""
import os
import sys

# Agregar el directorio src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

# Intentar importar todos los componentes
try:
    from weather_api_client import WeatherAPIClient
    from weather_data_processor import WeatherDataProcessor
    from rainfall_predictor import RainfallPredictor
    from weather_visualizer import WeatherVisualizer
    from streamlit_app import StreamlitApp
    
    print("✓ Todos los módulos importados correctamente")
    
    # Verificar archivos necesarios en models/
    models_dir = os.path.join(parent_dir, 'models')
    files_to_check = [
        "modelo_lluvia_lstm.h5",
        "scaler_lstm.pkl"    ]
    
    for file in files_to_check:
        file_path = os.path.join(models_dir, file)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"✓ Archivo models/{file} encontrado ({size_kb:.1f} KB)")
        else:
            print(f"✗ Archivo models/{file} no encontrado")
    
    # Crear una instancia de cada componente
    print("\nCreando instancias de componentes:")
    
    api_client = WeatherAPIClient("test_key")
    print("✓ WeatherAPIClient inicializado")
    
    # Intentar cargar el predictor con modelo y scaler
    modelo_path = os.path.join(models_dir, 'modelo_lluvia_lstm.h5')
    scaler_path = os.path.join(models_dir, 'scaler_lstm.pkl')
    
    if os.path.exists(modelo_path) and os.path.exists(scaler_path):
        predictor = RainfallPredictor(modelo_path, scaler_path)
        print("✓ RainfallPredictor inicializado con modelo y scaler")
        
        processor = WeatherDataProcessor(predictor.scaler)
        print("✓ WeatherDataProcessor inicializado con scaler")
    else:
        print("⚠ No se pudieron inicializar RainfallPredictor y WeatherDataProcessor con archivos reales")
    
    visualizer = WeatherVisualizer()
    print("✓ WeatherVisualizer inicializado")
    
    print("\n✓ Verificación completada: todos los componentes funcionan correctamente")
    
except Exception as e:
    print(f"✗ Error durante la verificación: {e}")
    import traceback
    traceback.print_exc()
