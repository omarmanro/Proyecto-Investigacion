# Manual de Usuario - Aplicación de Predicción de Lluvia

## Introducción

Esta aplicación utiliza inteligencia artificial para predecir la probabilidad de lluvia basándose en datos meteorológicos en tiempo real. La aplicación ha sido desarrollada de manera modular para facilitar su mantenimiento y extensibilidad.

## Requisitos del Sistema

- Python 3.7 o superior
- Conexión a Internet (para obtener datos meteorológicos en tiempo real)
- Bibliotecas requeridas (instalables mediante `pip install -r requirements.txt`):
  - streamlit
  - pandas
  - numpy
  - folium
  - streamlit-folium
  - plotly
  - matplotlib
  - seaborn
  - tensorflow
  - keras
  - scikit-learn

## Instalación

1. Clone o descargue el repositorio en su equipo local
2. Navegue hasta el directorio `py_modular`
3. Instale las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Ejecución de la Aplicación

Para iniciar la aplicación, ejecute el siguiente comando desde el directorio `py_modular`:

```bash
streamlit run app.py
```

Esto abrirá automáticamente su navegador web predeterminado con la aplicación cargada. Si no se abre automáticamente, acceda a la URL mostrada en la terminal (normalmente http://localhost:8501).

## Uso de la Aplicación

### 1. Selección de Ubicación

La aplicación se inicia mostrando un mapa interactivo y campos para ingresar coordenadas geográficas. Puede seleccionar una ubicación de dos maneras:

- **Mediante el mapa interactivo**: Haga clic en cualquier punto del mapa para seleccionar la ubicación deseada.
- **Mediante coordenadas**: Introduzca manualmente los valores de latitud y longitud en los campos correspondientes del panel lateral.

### 2. Obtención de Datos Climáticos

Una vez seleccionada la ubicación, haga clic en el botón "Obtener datos climáticos en tiempo real" del panel lateral. La aplicación:

1. Conectará con la API de OpenWeatherMap para obtener datos meteorológicos actuales
2. Procesará estos datos para su uso en el modelo de predicción
3. Utilizará el modelo LSTM para predecir la probabilidad de lluvia
4. Mostrará los resultados y diversas visualizaciones

### 3. Interpretación de Resultados

La aplicación muestra:

- **Datos Meteorológicos Actuales**: Temperatura, humedad, presión atmosférica, punto de rocío y velocidad del viento.
- **Resultado de la Predicción**: Probabilidad de lluvia expresada como porcentaje, con código de color (verde: baja, naranja: media, rojo: alta).
- **Visualizaciones**: Diversas representaciones gráficas de los datos meteorológicos y la predicción.

### 4. Visualizaciones Disponibles

La aplicación ofrece varias pestañas con diferentes visualizaciones:

- **Gráfico de Radar**: Compara múltiples variables meteorológicas.
- **Gráfico de Barras**: Muestra valores actuales de las principales variables.
- **Indicador de Probabilidad**: Muestra la probabilidad de lluvia en formato de medidor.
- **Datos Históricos**: Gráfica temporal de datos históricos o simulados.
- **Mapa de Calor**: Visualiza la correlación entre variables.
- **Diagrama de Dispersión**: Muestra la relación entre temperatura y probabilidad de lluvia.

## Solución de Problemas

### Error al obtener datos climáticos

Si aparece el mensaje "No se pudo obtener información climática para la ubicación seleccionada":

- Verifique su conexión a Internet
- Compruebe que las coordenadas seleccionadas corresponden a una ubicación válida
- Inténtelo nuevamente más tarde (posible límite de API alcanzado)

### Error al cargar el modelo

Si aparece el mensaje "No se encuentra el archivo del modelo":

- Asegúrese de que el archivo `modelo_lluvia_lstm.h5` está presente en el directorio `py_modular`
- Verifique que el archivo `scaler_lstm.pkl` está presente en el directorio `py_modular`

### Otras incidencias

Para otros problemas no documentados, puede consultar la sección "Información de depuración" que aparece expandible en la parte inferior de la aplicación.

## Personalización y Extensión

Esta aplicación ha sido diseñada de manera modular, lo que facilita su personalización y extensión:

- Modifique `weather_api_client.py` para cambiar o añadir fuentes de datos meteorológicos
- Ajuste `weather_data_processor.py` para modificar el procesamiento de datos
- Actualice `rainfall_predictor.py` para implementar algoritmos de predicción diferentes
- Edite `weather_visualizer.py` para añadir nuevas visualizaciones
- Personalice `streamlit_app.py` para cambiar la interfaz de usuario
