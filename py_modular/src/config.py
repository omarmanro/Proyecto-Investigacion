"""
Configuración centralizada para el proyecto de predicción de lluvia.
Maneja la carga de variables de entorno y configuraciones.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
import os
from pathlib import Path
# Cargar .env desde el directorio raíz del proyecto
project_root = Path(__file__).resolve().parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path)

class Config:
    """
    Clase de configuración que centraliza todas las variables de entorno
    y configuraciones del proyecto.
    """
    
    # Configuración de API de OpenWeatherMap
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # Configuración de Base de Datos SQL Server
    MSSQL_SERVER = os.getenv('MSSQL_SERVER', 'CHANG')
    MSSQL_DATABASE = os.getenv('MSSQL_DATABASE', 'MierdiInvestigacion')
    MSSQL_USERNAME = os.getenv('MSSQL_USERNAME', 'sa')
    MSSQL_PASSWORD = os.getenv('MSSQL_PASSWORD')
    MSSQL_DRIVER = os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    MSSQL_TRUST_CERTIFICATE = os.getenv('MSSQL_TRUST_CERTIFICATE', 'yes')
    MSSQL_TIMEOUT = int(os.getenv('MSSQL_TIMEOUT', '30'))

    # Configuración de Base de Datos PostgreSQL (Supabase)
    PG_SERVER = os.getenv('PG_SERVER')
    PG_PORT = os.getenv('PG_PORT', '5432')
    PG_DATABASE = os.getenv('PG_DATABASE', 'postgres')
    PG_USERNAME = os.getenv('PG_USERNAME', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD')    # Configuración de la aplicación
    APP_DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
    APP_PORT = int(os.getenv('APP_PORT', '8501'))
    
    # Configuración de modelos ML
    @classmethod
    def _get_base_dir(cls):
        """Obtiene el directorio base del proyecto."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @property
    def MODEL_PATH(self):
        """Ruta al archivo del modelo."""
        return os.getenv('MODEL_PATH', os.path.join(self._get_base_dir(), 'models', 'modelo_lluvia_lstm.h5'))
    
    @property
    def SCALER_PATH(self):
        """Ruta al archivo del scaler."""
        return os.getenv('SCALER_PATH', os.path.join(self._get_base_dir(), 'models', 'scaler_lstm.pkl'))
      # Configuración de ubicaciones por defecto
    DEFAULT_LATITUDE = float(os.getenv('DEFAULT_LATITUDE', '25.685194'))
    DEFAULT_LONGITUDE = float(os.getenv('DEFAULT_LONGITUDE', '-109.080806'))
    
    # Configuración de LLM (LM Studio)
    LLM_API_URL = os.getenv('LLM_API_URL', 'http://localhost:1234/v1')
    LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'l3-umbral-mind-rp-v0.3-8b')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1000'))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.4'))
    
    @classmethod
    def get_mssql_connection_string(cls):
        """
        Genera la cadena de conexión para la base de datos SQL Server.
        
        Returns:
            str: Cadena de conexión para SQLAlchemy
        """
        if not cls.MSSQL_PASSWORD:
            raise ValueError("MSSQL_PASSWORD no está configurada en las variables de entorno")
            
        return (
            f'mssql+pyodbc://{cls.MSSQL_USERNAME}:{cls.MSSQL_PASSWORD}@{cls.MSSQL_SERVER}/'
            f'{cls.MSSQL_DATABASE}?driver={cls.MSSQL_DRIVER.replace(" ", "+")}&'
            f'TrustServerCertificate={cls.MSSQL_TRUST_CERTIFICATE}&timeout={cls.MSSQL_TIMEOUT}'
        )
    
    @classmethod
    def get_pg_connection_string(cls):
        """
        Genera la cadena de conexión para PostgreSQL (Supabase).
        
        Returns:
            str: Cadena de conexión para SQLAlchemy
        """
        if not cls.PG_PASSWORD:
            raise ValueError("PG_PASSWORD no está configurada en las variables de entorno")
            
        return (
            f'postgresql://{cls.PG_USERNAME}:{cls.PG_PASSWORD}@{cls.PG_SERVER}:{cls.PG_PORT}/{cls.PG_DATABASE}'
        )

    @classmethod
    def validate_config(cls):
        """
        Valida que todas las configuraciones críticas estén presentes.
        
        Returns:
            tuple: (bool, list) - (es_valida, lista_de_errores)
        """
        errores = []
        
        if not cls.OPENWEATHER_API_KEY:
            errores.append("OPENWEATHER_API_KEY no está configurada")
            
        if not cls.MSSQL_PASSWORD:
            errores.append("MSSQL_PASSWORD no está configurada")
              # Verificar que los archivos del modelo existen usando las propiedades
        if not os.path.exists(cls().MODEL_PATH):
            errores.append(f"Archivo del modelo no encontrado: {cls().MODEL_PATH}")
            
        if not os.path.exists(cls().SCALER_PATH):
            errores.append(f"Archivo del scaler no encontrado: {cls().SCALER_PATH}")
        
        return len(errores) == 0, errores


# Instancia global de configuración
config = Config()

# Validar configuración al importar el módulo
is_valid, errors = config.validate_config()
if not is_valid:
    print("⚠️  Advertencias de configuración:")
    for error in errors:
        print(f"   - {error}")
