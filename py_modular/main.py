"""
Punto de entrada principal para la aplicación de predicción de lluvia.
Este archivo permite ejecutar la aplicación desde la raíz del proyecto.
"""

import sys
import os

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para ejecutar la aplicación Streamlit."""
    try:
        # Importar la aplicación principal
        from streamlit_app import StreamlitApp
        
        print("🚀 Iniciando aplicación de predicción de lluvia...")
        print("📁 Estructura organizada: src/, tests/, docs/, models/, scripts/")
        print("🌐 Abriendo en http://localhost:8501")
        
        # La aplicación se ejecutará automáticamente cuando Streamlit importe streamlit_app.py
        # Este archivo sirve como punto de entrada documentado
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("ℹ️  Para ejecutar la aplicación, usa:")
    print("   streamlit run src/streamlit_app.py")
    print("   O desde la raíz: python -m streamlit run src/streamlit_app.py")
    main()
