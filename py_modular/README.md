# Aplicación Modular de Predicción de Lluvia

Esta versión modularizada de la aplicación de predicción de lluvia ha sido estructurada siguiendo principios de diseño orientado a objetos para mejorar la organización, mantenibilidad y extensibilidad del código.

## Estructura del Proyecto

La aplicación se ha dividido en los siguientes módulos con responsabilidades específicas:

- **WeatherAPIClient**: Maneja las llamadas a la API de OpenWeatherMap para obtener datos meteorológicos.
- **WeatherDataProcessor**: Procesa y transforma los datos meteorológicos para su uso en el modelo de predicción.
- **RainfallPredictor**: Realiza predicciones de lluvia utilizando un modelo LSTM entrenado.
- **WeatherVisualizer**: Genera visualizaciones interactivas para representar los datos meteorológicos.
- **StreamlitApp**: Gestiona la interfaz de usuario y coordina todos los componentes.

## Requisitos

- Python 3.7 o superior
- Bibliotecas requeridas: streamlit, pandas, numpy, folium, streamlit-folium, plotly, matplotlib, seaborn, tensorflow, keras, scikit-learn

## Instalación

1. Clone este repositorio
2. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

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
