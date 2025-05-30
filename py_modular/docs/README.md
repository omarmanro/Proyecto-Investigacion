# Aplicación Modular de Predicción de Lluvia

Esta versión modularizada de la aplicación de predicción de lluvia ha sido estructurada siguiendo principios de diseño orientado a objetos para mejorar la organización, mantenibilidad y extensibilidad del código.

## Estructura del Proyecto

La aplicación se ha dividido en los siguientes módulos con responsabilidades específicas:

- **WeatherAPIClient**: Maneja las llamadas a la API de OpenWeatherMap para obtener datos meteorológicos.
- **WeatherDataProcessor**: Procesa y transforma los datos meteorológicos para su uso en el modelo de predicción.
- **RainfallPredictor**: Realiza predicciones de lluvia utilizando un modelo LSTM entrenado.
- **WeatherVisualizer**: Genera visualizaciones interactivas para representar los datos meteorológicos.
- **StreamlitApp**: Gestiona la interfaz de usuario y coordina todos los componentes.
- **Config**: Maneja la configuración centralizada y variables de entorno.

## Requisitos

- Python 3.7 o superior
- Bibliotecas requeridas: streamlit, pandas, numpy, folium, streamlit-folium, plotly, matplotlib, seaborn, tensorflow, keras, scikit-learn, python-dotenv

## Instalación

1. Clone este repositorio
2. Copie el archivo de configuración de ejemplo:
   ```
   cp .env.example .env
   ```
3. Edite el archivo `.env` con sus credenciales:
   - **OPENWEATHER_API_KEY**: Su clave API de OpenWeatherMap (obténgala gratis en https://openweathermap.org/api)
   - **DB_SERVER**: Servidor de la base de datos SQL Server
   - **DB_DATABASE**: Nombre de la base de datos
   - **DB_USERNAME**: Usuario de la base de datos
   - **DB_PASSWORD**: Contraseña de la base de datos
   - **MODEL_PATH**: Ruta al archivo del modelo LSTM entrenado
   - **SCALER_PATH**: Ruta al archivo del scaler
4. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Configuración de Variables de Entorno

La aplicación utiliza variables de entorno para manejar credenciales y configuraciones sensibles. Estas se cargan desde un archivo `.env` que no debe incluirse en el control de versiones.

### Variables Requeridas:

- `OPENWEATHER_API_KEY`: Clave API de OpenWeatherMap
- `DB_SERVER`: Servidor de base de datos
- `DB_DATABASE`: Nombre de la base de datos
- `DB_USERNAME`: Usuario de base de datos
- `DB_PASSWORD`: Contraseña de base de datos

### Variables Opcionales:

- `DB_DRIVER`: Driver de base de datos (por defecto: "SQL Server")
- `DB_TRUST_CERTIFICATE`: Confianza del certificado (por defecto: "yes")
- `DB_TIMEOUT`: Timeout de conexión (por defecto: 30)
- `APP_DEBUG`: Modo debug (por defecto: False)
- `APP_PORT`: Puerto de la aplicación (por defecto: 8501)
- `MODEL_PATH`: Ruta del modelo ML (por defecto: "./modelo_lluvia_lstm.h5")
- `SCALER_PATH`: Ruta del scaler (por defecto: "./scaler_lstm.pkl")
- `DEFAULT_LATITUDE`: Latitud por defecto (por defecto: 25.685194)
- `DEFAULT_LONGITUDE`: Longitud por defecto (por defecto: -109.080806)

## Ejecución de la Aplicación

Para ejecutar la aplicación, simplemente ejecute:

```
streamlit run app.py
```

## Funcionalidades

- Predicción de lluvia basada en datos meteorológicos en tiempo real
- Selección de ubicación mediante un mapa interactivo
- Utilización de datos históricos desde la base de datos cuando la API no está disponible
- Visualizaciones variadas de datos meteorológicos:
  - Gráfico de radar para comparar variables meteorológicas
  - Gráfico de barras para visualizar valores actuales
  - Indicador tipo gauge para mostrar la probabilidad de lluvia
  - Línea de tiempo para datos históricos
  - Mapa de calor para visualizar correlaciones entre variables
  - Diagrama de dispersión para analizar relaciones

## Extensión y Personalización

La estructura modular facilita la extensión y personalización de la aplicación:

- Para añadir nuevos tipos de visualizaciones, modifique la clase `WeatherVisualizer`
- Para mejorar el modelo de predicción, modifique la clase `RainfallPredictor`
- Para implementar nuevas fuentes de datos, modifique la clase `WeatherAPIClient`
- Para añadir funcionalidades a la interfaz, modifique la clase `StreamlitApp`
