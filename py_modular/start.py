"""
Script de inicio rápido para la aplicación de predicción de lluvia.
Este script realiza todas las verificaciones necesarias y luego inicia la aplicación en el puerto 3000.
"""
import os
import sys
import subprocess
from pathlib import Path

def iniciar_aplicacion():
    """
    Inicia la aplicación con todas las configuraciones necesarias
    """
    # Obtener ruta al directorio del proyecto
    project_root = Path(__file__).resolve().parent
    
    print("=" * 60)
    print("🚀 INICIANDO APLICACIÓN DE PREDICCIÓN DE LLUVIA")
    print("=" * 60)
    print(f"📁 Directorio del proyecto: {project_root}")
    
    # Verificar archivos del modelo
    print("\n1️⃣ Verificando archivos del modelo...")
    validation_script = project_root / 'validar_archivos.py'
    result = subprocess.run([sys.executable, str(validation_script)], 
                           capture_output=True, text=True, check=False)
    
    if result.returncode != 0:
        print(f"❌ Error al validar archivos del modelo:")
        print(result.stdout)
        print(result.stderr)
        return False
    else:
        print(result.stdout)
    
    # Intentar liberar el puerto 3000
    print("\n2️⃣ Preparando el puerto 3000...")
    try:
        if sys.platform == 'win32':
            # En Windows
            cmd = "Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            subprocess.run(["powershell", "-Command", cmd], 
                         capture_output=True, check=False)
        else:
            # En Linux/Mac
            subprocess.run("kill $(lsof -t -i:3000) 2>/dev/null || true", 
                         shell=True, check=False)
        print("✅ Puerto liberado o no estaba en uso")
    except Exception as e:
        print(f"⚠️ No se pudo liberar el puerto: {e}")
    
    # Configurar variables de entorno
    print("\n3️⃣ Configurando el entorno...")
    env = os.environ.copy()
    env['STREAMLIT_SERVER_PORT'] = '3000'
    
    # Configurar el path de Python para incluir el directorio src
    app_path = project_root / 'app.py'
    
    # Iniciar la aplicación
    print("\n4️⃣ Iniciando la aplicación en http://localhost:3000")
    try:
        # Usar app.py con las correcciones implementadas
        subprocess.run([sys.executable, "-m", "streamlit", "run", 
                      str(app_path), "--server.port=3000"], 
                     env=env, cwd=str(project_root), check=False)
        return True
    except KeyboardInterrupt:
        print("\n⏹️ Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        return False

if __name__ == "__main__":
    iniciar_aplicacion()
