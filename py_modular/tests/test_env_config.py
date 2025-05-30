"""
Script para probar la configuración de variables de entorno.
Ejecuta este script para verificar que todas las variables están configuradas correctamente.
"""
import os
import sys

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config

def test_configuracion():
    """
    Prueba que todas las configuraciones críticas estén correctamente establecidas.
    """
    print("🔧 Probando configuración de variables de entorno...")
    print("=" * 60)
    
    # Validar configuración
    is_valid, errors = config.validate_config()
    
    if is_valid:
        print("✅ Todas las configuraciones son válidas")
    else:
        print("❌ Se encontraron errores en la configuración:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("\n📋 Configuración actual:")
    print("-" * 40)
    
    # API Configuration
    print("🌦️  OpenWeatherMap API:")
    api_key = config.OPENWEATHER_API_KEY
    if api_key:
        print(f"   API Key: {api_key[:8]}...")
    else:
        print("   API Key: ❌ No configurada")
    
    # Database Configuration
    print("\n🗄️  Base de Datos:")
    print(f"   Servidor: {config.DB_SERVER}")
    print(f"   Base de datos: {config.DB_DATABASE}")
    print(f"   Usuario: {config.DB_USERNAME}")
    print(f"   Driver: {config.DB_DRIVER}")
    print(f"   Timeout: {config.DB_TIMEOUT}s")
    
    # App Configuration
    print("\n🎛️  Aplicación:")
    print(f"   Debug: {config.APP_DEBUG}")
    print(f"   Puerto: {config.APP_PORT}")
    
    # ML Configuration
    print("\n🧠 Modelos ML:")
    print(f"   Modelo: {config.MODEL_PATH}")
    print(f"   Scaler: {config.SCALER_PATH}")
    
    # Default Location
    print("\n📍 Ubicación por defecto:")
    print(f"   Latitud: {config.DEFAULT_LATITUDE}")
    print(f"   Longitud: {config.DEFAULT_LONGITUDE}")
    
    # Test database connection
    print("\n🔗 Probando conexión a base de datos...")
    try:
        connection_string = config.get_db_connection_string()
        print("   ✅ Cadena de conexión generada correctamente")
        print(f"   Cadena: {connection_string.split('@')[0]}@[OCULTO]")
    except Exception as e:
        print(f"   ❌ Error al generar cadena de conexión: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Configuración completada exitosamente")
    return True

def test_importaciones():
    """
    Prueba que todos los módulos se puedan importar correctamente.
    """
    print("\n📦 Probando importaciones de módulos...")
    print("-" * 40)
    
    try:
        from weather_api_client import WeatherAPIClient
        print("   ✅ WeatherAPIClient importado")
        
        from weather_data_processor import WeatherDataProcessor
        print("   ✅ WeatherDataProcessor importado")
        
        from rainfall_predictor import RainfallPredictor
        print("   ✅ RainfallPredictor importado")
        
        from weather_visualizer import WeatherVisualizer
        print("   ✅ WeatherVisualizer importado")
        
        from streamlit_app import StreamlitApp
        print("   ✅ StreamlitApp importado")
        
        print("   ✅ Todas las importaciones exitosas")
        return True
        
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de configuración...")
    
    # Test configuración
    config_ok = test_configuracion()
    
    # Test importaciones
    import_ok = test_importaciones()
    
    # Resultado final
    print("\n" + "🔍 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    if config_ok and import_ok:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("💡 La aplicación está lista para ejecutarse con:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revise la configuración.")
        print("📚 Consulte el README.md para más información.")
    
    print("=" * 60)
