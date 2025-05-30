#!/usr/bin/env python3
"""
Script para ejecutar la aplicación desde cualquier directorio.
Maneja las rutas correctamente para la nueva estructura de carpetas.
"""

import os
import sys
import subprocess

def run_application():
    """Ejecuta la aplicación Streamlit con las rutas correctas."""
    
    # Obtener el directorio raíz del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, 'src')
    
    # Cambiar al directorio del proyecto
    os.chdir(project_root)    
    print("🚀 INICIANDO APLICACIÓN DE PREDICCIÓN DE LLUVIA")
    print("=" * 50)
    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"📂 Directorio de código fuente: {src_dir}")
    print("🌐 La aplicación se abrirá en: http://localhost:3000")
    print("=" * 50)
    
    # Verificar que streamlit está instalado
    try:
        import streamlit
        print("✅ Streamlit encontrado")
    except ImportError:
        print("❌ Streamlit no está instalado")
        print("💡 Instala las dependencias: pip install -r requirements.txt")
        return False
      # Verificar que los archivos necesarios existen
    streamlit_app_path = os.path.join(src_dir, 'streamlit_app.py')
    if not os.path.exists(streamlit_app_path):
        print(f"❌ No se encontró: {streamlit_app_path}")
        return False
    
    print("✅ Verificando archivos del modelo...")
    # Ejecutar el script de validación de archivos
    validation_script = os.path.join(project_root, 'validar_archivos.py')
    result = subprocess.run([sys.executable, validation_script], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error al validar archivos del modelo:")
        print(result.stdout)
        print(result.stderr)
        return False
    else:
        print(result.stdout)
    
    # Intentar liberar el puerto 3000 antes de ejecutar la aplicación
    try:
        print("🔄 Intentando liberar el puerto 3000...")
        if sys.platform == 'win32':
            # En Windows
            subprocess.run(["powershell", "-Command", 
                           "Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"], 
                           capture_output=True)
        else:
            # En Linux/Mac
            subprocess.run(["kill", "$(lsof -t -i:3000)"], shell=True, capture_output=True)
        print("✅ Puerto liberado o no estaba en uso")
    except Exception as e:
        print(f"⚠️ No se pudo liberar el puerto: {e}")
    
    # Configurar la variable de entorno para evitar la advertencia de puerto reservado
    os.environ['STREAMLIT_SERVER_PORT'] = '3000'
    
    print("🚀 Ejecutando aplicación...")    # Ejecutar streamlit
    try:
        # Configurar variables de entorno para el proceso
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = '3000'
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'  # Evita abrir automáticamente el navegador
        
        cmd = [sys.executable, '-m', 'streamlit', 'run', os.path.join('src', 'streamlit_app.py'), '--server.port=3000']
        subprocess.run(cmd, cwd=project_root, env=env)
        return True
    except KeyboardInterrupt:
        print("\n⏹️ Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        return False

def run_tests():
    """Ejecuta los tests de la aplicación."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(project_root, 'tests')
    
    print("🧪 EJECUTANDO TESTS")
    print("=" * 30)
    
    # Cambiar al directorio del proyecto
    os.chdir(project_root)
    
    # Ejecutar test de configuración
    config_test = os.path.join(tests_dir, 'test_env_config.py')
    if os.path.exists(config_test):
        print("🔧 Ejecutando test de configuración...")
        try:
            subprocess.run([sys.executable, config_test], cwd=project_root)
        except Exception as e:
            print(f"❌ Error en test de configuración: {e}")
    
    print("✅ Tests completados")

def show_help():
    """Muestra la ayuda del script."""
    print("🔧 EJECUTOR DE APLICACIÓN DE PREDICCIÓN DE LLUVIA")
    print("=" * 50)
    print("Comandos disponibles:")
    print("  python run.py app    - Ejecutar la aplicación")
    print("  python run.py test   - Ejecutar tests")
    print("  python run.py help   - Mostrar esta ayuda")
    print("\nEstructura del proyecto:")
    print("  📁 src/     - Código fuente principal")
    print("  📁 tests/   - Pruebas y validaciones")
    print("  📁 docs/    - Documentación")
    print("  📁 models/  - Modelos ML entrenados")
    print("  📁 scripts/ - Scripts utilitarios")

def main():
    """Función principal del ejecutor."""
    if len(sys.argv) < 2:
        command = 'app'  # Comando por defecto
    else:
        command = sys.argv[1].lower()
    
    if command == 'app':
        success = run_application()
        sys.exit(0 if success else 1)
    elif command == 'test':
        run_tests()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Comando desconocido: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
