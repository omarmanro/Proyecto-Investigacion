"""
Punto de entrada principal para la aplicación modular de predicción de lluvia.
Este archivo simplemente importa e inicializa la aplicación Streamlit modularizada.
"""
from streamlit_app import StreamlitApp

if __name__ == "__main__":
    # Crear instancia de la aplicación
    app = StreamlitApp()
    
    # Ejecutar la aplicación
    app.run()
