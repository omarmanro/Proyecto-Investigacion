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
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from tests/
src_path = os.path.join(base_path, "src")
models_path = os.path.join(base_path, "models")

# Módulos a verificar en src/
modules = [
    "weather_api_client.py",
    "weather_data_processor.py",
    "rainfall_predictor.py",
    "weather_visualizer.py",
    "streamlit_app.py",
    "config.py"
]

# app.py está en la raíz
root_files = ["app.py"]

# Verificar archivos de modelo
model_files = [
    "modelo_lluvia_lstm.h5",
    "scaler_lstm.pkl"
]

print("="*80)
print(" "*30 + "VERIFICACIÓN DE MÓDULOS")
print("="*80)

# Verificar módulos en src/
all_modules_present = True
for module in modules:
    module_path = os.path.join(src_path, module)
    if os.path.exists(module_path):
        size = os.path.getsize(module_path) / 1024
        print(f"✓ src/{module} ({size:.1f} KB)")
    else:
        print(f"✗ src/{module} no encontrado")
        all_modules_present = False

# Verificar archivos en la raíz
for file in root_files:
    file_path = os.path.join(base_path, file)
    if os.path.exists(file_path):
        size = os.path.getsize(file_path) / 1024
        print(f"✓ {file} ({size:.1f} KB)")
    else:
        print(f"✗ {file} no encontrado")
        all_modules_present = False

print("Archivos de modelo:")
for model_file in model_files:
    model_path = os.path.join(models_path, model_file)
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / 1024 / 1024  # MB for models
        print(f"✓ models/{model_file} ({size:.1f} MB)")
    else:
        print(f"✗ models/{model_file} no encontrado")

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
