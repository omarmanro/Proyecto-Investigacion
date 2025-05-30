"""
Punto de entrada principal para la aplicación modular de predicción de lluvia.
Este archivo simplemente importa e inicializa la aplicación Streamlit modularizada.
"""
import os
import sys

# Agregar el directorio principal del proyecto al path de Python
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

# Configurar puerto 3000 ANTES de importar streamlit
os.environ['STREAMLIT_SERVER_PORT'] = '3000'

# Importar después de configurar el path y el puerto
from src.streamlit_app import StreamlitApp

if __name__ == "__main__":
    # Crear instancia de la aplicación
    app = StreamlitApp()
    
    # Ejecutar la aplicación
    app.run()
