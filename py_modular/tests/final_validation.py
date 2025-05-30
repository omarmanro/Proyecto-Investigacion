#!/usr/bin/env python3
"""
Script de validación final para verificar que la migración a variables de entorno
está completa y funcionando correctamente.
"""

import os
import sys

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar la clase Config y crear una instancia
from src.config import Config
config = Config()

def print_section(title):
    """Imprime una sección con formato."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def validate_env_variables():
    """Valida que todas las variables de entorno están configuradas."""
    print_section("VALIDACIÓN DE VARIABLES DE ENTORNO")
    
    required_vars = [
        'OPENWEATHER_API_KEY',
        'DB_SERVER', 
        'DB_DATABASE',
        'DB_USERNAME',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not hasattr(config, var) or not getattr(config, var):
            missing_vars.append(var)
        else:
            value = getattr(config, var)
            # Ocultar valores sensibles
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = value[:8] + '...' if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    else:
        print(f"\n✅ Todas las variables de entorno están configuradas")
        return True

def validate_config_usage():
    """Valida que los archivos estén usando la configuración correctamente."""
    print_section("VALIDACIÓN DE USO DE CONFIGURACIÓN")
    
    # Definir rutas correctas para archivos en src/
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    tests_dir = os.path.dirname(__file__)
    
    files_to_check = [
        (os.path.join(src_dir, 'streamlit_app.py'), 'streamlit_app.py'),
        (os.path.join(src_dir, 'weather_api_client.py'), 'weather_api_client.py'),
        (os.path.join(src_dir, 'weather_data_processor.py'), 'weather_data_processor.py'),
        (os.path.join(tests_dir, 'test_components.py'), 'test_components.py')
    ]
    
    issues = []
    
    for file_path, file_name in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar que importa config
            if 'from config import config' in content or 'import config' in content:
                print(f"✅ {file_name}: Importa configuración")
            else:
                print(f"⚠️  {file_name}: No importa configuración")
                issues.append(f"{file_name} no importa config")
                
            # Verificar que no tiene credenciales hardcodeadas
            hardcoded_patterns = [
                'e63d503e181ce2fd667ad05b4aaed60c',  # API key
                'CHANG',  # Server (en contexto de conexión)
                'MierdiInvestigacion',  # Database name
                'sa',  # Username (en contexto de conexión)
                'Once'  # Password
            ]
            
            found_hardcoded = []
            for pattern in hardcoded_patterns:
                if pattern in content:
                    # Verificar si está en un comentario o string de configuración legítimo
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and not (
                            line.strip().startswith('#') or 
                            'config.' in line or
                            '.env' in file_name
                        ):
                            found_hardcoded.append(f"{pattern} en línea {i+1}")
            
            if found_hardcoded:
                print(f"⚠️  {file_name}: Posibles credenciales hardcodeadas: {found_hardcoded}")
                issues.extend(found_hardcoded)
            else:
                print(f"✅ {file_name}: Sin credenciales hardcodeadas")
        else:
            print(f"❌ {file_name}: Archivo no encontrado")
            issues.append(f"{file_name} no encontrado")
    
    return len(issues) == 0, issues

def validate_file_structure():
    """Valida que los archivos necesarios existen."""
    print_section("VALIDACIÓN DE ESTRUCTURA DE ARCHIVOS")
    
    # Definir rutas correctas para la nueva estructura
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    required_files = [
        ('.env', os.path.join(project_root, '.env')),
        ('.env.example', os.path.join(project_root, '.env.example')),
        ('config.py', os.path.join(project_root, 'src', 'config.py')),
        ('.gitignore', os.path.join(project_root, '.gitignore'))
    ]
    
    missing_files = []
    for file_name, file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_name}: Existe")
        else:
            print(f"❌ {file_name}: No encontrado")
            missing_files.append(file_name)
    
    return len(missing_files) == 0, missing_files

def test_config_functionality():
    """Prueba la funcionalidad de la configuración."""
    print_section("PRUEBA DE FUNCIONALIDAD DE CONFIGURACIÓN")
    
    try:
        # Probar validación de configuración
        is_valid, errors = config.validate_config()
        if is_valid:
            print("✅ Validación de configuración: PASÓ")
        else:
            print(f"❌ Validación de configuración: FALLÓ - {errors}")
            return False
            
        # Probar generación de cadenas de conexión
        db_string = config.get_db_connection_string()
        if db_string and 'mssql+pyodbc://' in db_string:
            print("✅ Generación de cadena DB: PASÓ")
        else:
            print("❌ Generación de cadena DB: FALLÓ")
            return False
            
        pyodbc_string = config.get_pyodbc_connection_string()
        if pyodbc_string and 'DRIVER=' in pyodbc_string:
            print("✅ Generación de cadena PyODBC: PASÓ")
        else:
            print("❌ Generación de cadena PyODBC: FALLÓ")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error al probar configuración: {e}")
        return False

def main():
    """Función principal de validación."""
    print("🚀 VALIDACIÓN FINAL DE MIGRACIÓN A VARIABLES DE ENTORNO")
    print("🗓️  Fecha: 26 de Mayo, 2025")
    
    # Ejecutar todas las validaciones
    env_valid = validate_env_variables()
    config_valid, config_issues = validate_config_usage()
    files_valid, missing_files = validate_file_structure()
    func_valid = test_config_functionality()
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    if env_valid and config_valid and files_valid and func_valid:
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("✅ Todas las validaciones pasaron")
        print("✅ Variables de entorno configuradas")
        print("✅ Archivos usan configuración centralizada")
        print("✅ Estructura de archivos correcta")
        print("✅ Funcionalidad de configuración operativa")
        print("\n💡 La aplicación está lista para producción")
        print("🚀 Para ejecutar: streamlit run streamlit_app.py")
        return True
    else:
        print("⚠️ MIGRACIÓN INCOMPLETA - Se encontraron problemas:")
        if not env_valid:
            print("❌ Variables de entorno incompletas")
        if not config_valid:
            print(f"❌ Problemas en uso de configuración: {config_issues}")
        if not files_valid:
            print(f"❌ Archivos faltantes: {missing_files}")
        if not func_valid:
            print("❌ Funcionalidad de configuración con errores")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
