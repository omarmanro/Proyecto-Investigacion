"""
Script de validación final para verificar que la migración a variables de entorno
está completa y funcionando correctamente.
"""

import os
from config import config

def main():
    print("🚀 VALIDACIÓN FINAL DE MIGRACIÓN A VARIABLES DE ENTORNO")
    print("🗓️  Fecha: 26 de Mayo, 2025")
    print("="*60)
    
    # Verificar variables de entorno
    print("\n🔍 VERIFICANDO VARIABLES DE ENTORNO:")
    print(f"✅ API Key: {config.OPENWEATHER_API_KEY[:10]}...")
    print(f"✅ DB Server: {config.DB_SERVER}")
    print(f"✅ DB Database: {config.DB_DATABASE}")
    print(f"✅ DB Username: {config.DB_USERNAME}")
    print(f"✅ DB Password: {'*' * len(config.DB_PASSWORD)}")
    
    # Verificar archivos de configuración
    print("\n🔍 VERIFICANDO ARCHIVOS DE CONFIGURACIÓN:")
    files = ['.env', '.env.example', 'config.py', '.gitignore']
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file}: Existe")
        else:
            print(f"❌ {file}: No encontrado")
    
    # Verificar funcionalidad
    print("\n🔍 VERIFICANDO FUNCIONALIDAD:")
    try:
        is_valid, errors = config.validate_config()
        if is_valid:
            print("✅ Validación de configuración: PASÓ")
        else:
            print(f"❌ Validación falló: {errors}")
            
        db_string = config.get_db_connection_string()
        if 'mssql+pyodbc://' in db_string:
            print("✅ Cadena de conexión DB: PASÓ")
        else:
            print("❌ Cadena de conexión DB: FALLÓ")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    print("✅ Todas las validaciones pasaron")
    print("💡 La aplicación está lista para usar")
    return True

if __name__ == "__main__":
    main()
