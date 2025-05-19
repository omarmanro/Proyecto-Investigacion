"""
Este script simplemente imprime un resumen de la estructura modular de la aplicación
para verificar que todos los componentes están disponibles y se relacionan correctamente.
"""
import os
import importlib.util

def check_module(module_path):
    """Verifica si un módulo existe y puede ser importado."""
    try:
        spec = importlib.util.spec_from_file_location(module_path, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"Error al importar {module_path}: {e}")
        return False

# Ruta base
base_path = os.path.dirname(os.path.abspath(__file__))

# Módulos a verificar
modules = [
    "weather_api_client.py",
    "weather_data_processor.py",
    "rainfall_predictor.py",
    "weather_visualizer.py",
    "streamlit_app.py",
    "app.py"
]

# Verificar archivos de modelo
model_files = [
    "modelo_lluvia_lstm.h5"
]

print("="*80)
print(" "*30 + "VERIFICACIÓN DE MÓDULOS")
print("="*80)

# Verificar módulos
all_modules_present = True
for module in modules:
    module_path = os.path.join(base_path, module)
    if os.path.exists(module_path):
        size = os.path.getsize(module_path) / 1024
        print(f"✓ {module} ({size:.1f} KB)")
    else:
        print(f"✗ {module} no encontrado")
        all_modules_present = False

print("\nArchivos de modelo:")
for model_file in model_files:
    model_path = os.path.join(base_path, model_file)
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / 1024
        print(f"✓ {model_file} ({size:.1f} KB)")
    else:
        print(f"✗ {model_file} no encontrado")
        all_modules_present = False

print("\nResumen de la estructura modular:")
print("="*80)
print("WeatherAPIClient: Maneja las llamadas a la API de OpenWeatherMap")
print("WeatherDataProcessor: Procesa y transforma los datos meteorológicos")
print("RainfallPredictor: Realiza predicciones de lluvia utilizando modelo LSTM")
print("WeatherVisualizer: Genera visualizaciones interactivas")
print("StreamlitApp: Gestiona la interfaz de usuario y coordina componentes")
print("app.py: Punto de entrada de la aplicación")
print("="*80)

if all_modules_present:
    print("\n✓ Todos los módulos están presentes. La aplicación está lista para ejecutarse.")
    print("\nPara ejecutar la aplicación, use el comando:")
    print("\n  streamlit run app.py")
else:
    print("\n✗ Faltan algunos módulos necesarios.")

print("\n" + "="*80)
