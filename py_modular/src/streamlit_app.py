"""
Aplicación principal de Streamlit que integra todas las funcionalidades.
"""
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import folium
from typing import Dict, Any
from streamlit_folium import st_folium

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weather_data_processor import WeatherDataProcessor
from weather_api_client import WeatherAPIClient
from rainfall_predictor import RainfallPredictor
from weather_visualizer import WeatherVisualizer
from model_metrics import ModelMetrics
from config import config

# Importación condicional del LLM client
try:
    from llm_client_new import LLMClient
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ LLMClient no disponible. Funcionalidad LLM deshabilitada.")

class StreamlitApp:
    """
    Clase principal que gestiona la aplicación de Streamlit y coordina
    todos los componentes.
    """
    def __init__(self):
        """
        Inicializa la aplicación y carga todos los componentes necesarios.
        """
        # Validar configuración
        is_valid, errors = config.validate_config()
        if not is_valid:
            st.error("Error en la configuración:")
            for error in errors:
                st.error(f"- {error}")
            st.stop()
            
        # Inicializar componentes usando configuración
        self.predictor = self._inicializar_predictor()
        self.api_client = WeatherAPIClient(config.OPENWEATHER_API_KEY)
        self.data_processor = WeatherDataProcessor(self.predictor.scaler)
        self.visualizer = WeatherVisualizer()
        self.model_metrics = ModelMetrics(self.predictor)
        
        # Inicializar cliente LLM si está disponible
        if LLM_AVAILABLE:
            self.llm_client = LLMClient()
        else:
            self.llm_client = None
            
        # Inicializar estado de la sesión
        self._inicializar_session_state()
        
    def _inicializar_predictor(self):
        """
        Inicializa el predictor de lluvia cargando el modelo y el scaler.
        
        Returns:
            RainfallPredictor: Instancia del predictor.
        """        
        # Usar rutas de configuración
        modelo_path = config.MODEL_PATH
        scaler_path = config.SCALER_PATH
        
        # Comprobar si los archivos existen
        if not os.path.exists(modelo_path):
            st.error(f"No se encuentra el archivo del modelo en {modelo_path}")
            # Intentar buscar en directorio raíz
            alt_modelo_path = '../../modelo_lluvia_lstm.h5'
            if os.path.exists(alt_modelo_path):
                modelo_path = alt_modelo_path
                st.info(f"Usando modelo alternativo en {modelo_path}")
                
        if not os.path.exists(scaler_path):
            st.error(f"No se encuentra el archivo del scaler en {scaler_path}")
            # Intentar buscar en directorio raíz
            alt_scaler_path = '../../scaler_lstm.pkl'
            if os.path.exists(alt_scaler_path):
                scaler_path = alt_scaler_path
                st.info(f"Usando scaler alternativo en {scaler_path}")
            
        return RainfallPredictor(modelo_path, scaler_path)
    
    def _inicializar_session_state(self):
        """
        Inicializa variables en el estado de la sesión de Streamlit.
        """
        if "lat" not in st.session_state:
            st.session_state.lat = config.DEFAULT_LATITUDE
        if "lon" not in st.session_state:
            st.session_state.lon = config.DEFAULT_LONGITUDE
        # Inicializar estado para modo de entrada personalizada
        if "use_custom_data" not in st.session_state:
            st.session_state.use_custom_data = False
        # Valores personalizados por defecto
        if "custom_temp" not in st.session_state:
            st.session_state.custom_temp = 25.0
        if "custom_humidity" not in st.session_state:
            st.session_state.custom_humidity = 60.0
        if "custom_pressure" not in st.session_state:
            st.session_state.custom_pressure = 1013.0
        if "custom_dew_point" not in st.session_state:
            st.session_state.custom_dew_point = 15.0
        if "custom_wind_speed" not in st.session_state:
            st.session_state.custom_wind_speed = 3.0
        if "custom_wind_direction" not in st.session_state:
            st.session_state.custom_wind_direction = 180.0
            
    def run(self):
        """
        Ejecuta la aplicación principal de Streamlit.
        """
        st.title("Predicción de Lluvia con IA")
        
        # Crear pestañas principales
        tab1, tab2 = st.tabs(["🌧️ Predicción", "📊 Desempeño del Modelo"])
        
        with tab1:
            # Crear panel lateral para controles
            self._crear_sidebar()
            
            # Mostrar mapa para seleccionar ubicación
            self._mostrar_mapa_seleccion()
            
            # Procesar datos si se solicita
            if st.session_state.get('procesar_datos', False):
                self._obtener_y_procesar_datos()
        
        with tab2:
            # Mostrar métricas del modelo
            self._mostrar_metricas_modelo()
            
    def _mostrar_metricas_modelo(self):
        """
        Muestra las métricas de desempeño del modelo LSTM.
        """
        st.header("📊 Desempeño del Modelo LSTM")
        
        # Opción para refrescar métricas
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Evaluación cuantitativa del rendimiento del modelo de predicción de lluvia**")
        with col2:
            refresh_metrics = st.button("🔄 Actualizar Métricas", help="Recalcular métricas con nuevos datos de prueba")
        
        # Obtener métricas del caché
        try:
            metrics_data = self.model_metrics.get_cached_metrics(force_refresh=refresh_metrics)
            
            # Extraer datos
            y_true = metrics_data['data']['y_true']
            y_pred = metrics_data['data']['y_pred']
            y_prob = metrics_data['data']['y_prob']
            
            # Mostrar reporte completo de métricas
            self.model_metrics.display_metrics_report(y_true, y_pred, y_prob)
            
        except Exception as e:
            st.error(f"Error al cargar métricas del modelo: {e}")
            st.info("Intentando generar métricas simuladas...")
            
            # Fallback: generar datos simulados simples
            try:
                np.random.seed(42)
                n_samples = 500
                y_true = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
                y_prob = np.random.beta(2, 5, n_samples)
                y_pred = (y_prob > 0.5).astype(int)
                
                # Mostrar métricas con datos simulados
                self.model_metrics.display_metrics_report(y_true, y_pred, y_prob)
                
                st.warning("⚠️ Métricas mostradas son simuladas. Verifique la configuración del modelo.")
                
            except Exception as e2:
                st.error(f"Error crítico en el sistema de métricas: {e2}")
                
    def _crear_sidebar(self):
        """
        Crea el panel lateral con controles para la aplicación.
        """
        st.sidebar.header("Ubicación geográfica")
        # Inputs para coordenadas (solo para mostrar valores actuales)
        st.sidebar.number_input(
            "Latitud", 
            value=st.session_state.lat, 
            format="%.6f", 
            key="lat_input",
            disabled=True
        )
        st.sidebar.number_input(
            "Longitud", 
            value=st.session_state.lon, 
            format="%.6f", 
            key="lon_input",
            disabled=True
        )
        
        # Opciones de entrada de datos
        st.sidebar.header("Opciones de datos")
        
        # Toggle para usar datos personalizados
        use_custom = st.sidebar.checkbox(
            "Usar datos personalizados", 
            value=st.session_state.use_custom_data,
            help="Active esta opción para ingresar datos meteorológicos manualmente"
        )
        st.session_state.use_custom_data = use_custom
        
        # Si se activa la opción de datos personalizados
        if st.session_state.use_custom_data:
            st.sidebar.subheader("Datos meteorológicos personalizados")
            
            # Temperatura
            st.session_state.custom_temp = st.sidebar.slider(
                "Temperatura (°C)", 
                min_value=-20.0,
                max_value=50.0,
                value=st.session_state.custom_temp,
                step=0.1
            )
            
            # Humedad
            st.session_state.custom_humidity = st.sidebar.slider(
                "Humedad (%)", 
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.custom_humidity,
                step=1.0
            )
            
            # Presión
            st.session_state.custom_pressure = st.sidebar.slider(
                "Presión (hPa)", 
                min_value=950.0,
                max_value=1050.0,
                value=st.session_state.custom_pressure,
                step=0.1
            )
            
            # Punto de rocío
            st.session_state.custom_dew_point = st.sidebar.slider(
                "Punto de rocío (°C)", 
                min_value=-30.0,
                max_value=35.0,
                value=st.session_state.custom_dew_point,
                step=0.1
            )
            
            # Velocidad del viento
            st.session_state.custom_wind_speed = st.sidebar.slider(
                "Velocidad del viento (m/s)", 
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.custom_wind_speed,
                step=0.1
            )
            
            # Dirección del viento
            st.session_state.custom_wind_direction = st.sidebar.slider(
                "Dirección del viento (°)", 
                min_value=0.0,
                max_value=360.0,
                value=st.session_state.custom_wind_direction,
                step=1.0            )
            
            # Botón para procesar datos personalizados
            if st.sidebar.button("Procesar datos personalizados"):
                st.session_state.procesar_datos = True
        else:
            # Botón para obtener datos reales
            if st.sidebar.button("Obtener datos climáticos en tiempo real"):
                st.session_state.procesar_datos = True
            else:
                st.session_state.procesar_datos = False
            
    def _mostrar_mapa_seleccion(self):
        """
        Muestra un mapa interactivo para seleccionar la ubicación con capas meteorológicas de OpenWeatherMap.
        """
        st.subheader("Seleccione una ubicación en el mapa")
        
        # Controles de capas meteorológicas
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Haga clic en el mapa para seleccionar una ubicación**")
            
        with col2:
            # Selector de capas meteorológicas
            capas_disponibles = {
                "Ninguna": None,
                "🌧️ Precipitación": "precipitation_new",
                "☁️ Nubosidad": "clouds_new", 
                "🌡️ Temperatura": "temp_new",
                "💨 Presión": "pressure_new",
                "💨 Viento": "wind_new"
            }
            
            capa_seleccionada = st.selectbox(
                "Capa meteorológica:",
                options=list(capas_disponibles.keys()),
                index=0,
                help="Seleccione una capa meteorológica para visualizar en el mapa"
            )
        
        # Crear mapa base con folium
        m = folium.Map(
            location=[st.session_state.lat, st.session_state.lon], 
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Añadir popup para coordenadas
        m.add_child(folium.LatLngPopup())
        
        # Añadir capa meteorológica de OpenWeatherMap si está seleccionada
        if capa_seleccionada != "Ninguna" and config.OPENWEATHER_API_KEY:
            capa_codigo = capas_disponibles[capa_seleccionada]
            
            # URL de la capa de OpenWeatherMap
            owm_url = f"http://tile.openweathermap.org/map/{capa_codigo}/{{z}}/{{x}}/{{y}}.png?appid={config.OPENWEATHER_API_KEY}"
            
            # Añadir la capa al mapa
            folium.raster_layers.TileLayer(
                tiles=owm_url,
                name=capa_seleccionada,
                overlay=True,
                control=True,
                opacity=0.6,
                attr="© OpenWeatherMap"
            ).add_to(m)
            
            # Información sobre la capa seleccionada
            info_capas = {
                "🌧️ Precipitación": "Muestra la intensidad de precipitación en tiempo real",
                "☁️ Nubosidad": "Visualiza la cobertura de nubes en la región",
                "🌡️ Temperatura": "Presenta la distribución de temperaturas",
                "💨 Presión": "Indica la presión atmosférica en diferentes zonas",
                "💨 Viento": "Muestra la velocidad y dirección del viento"
            }
            
            st.info(f"**{capa_seleccionada}**: {info_capas.get(capa_seleccionada, '')}")
        
        elif capa_seleccionada != "Ninguna" and not config.OPENWEATHER_API_KEY:
            st.warning("⚠️ API Key de OpenWeatherMap no configurada. No se pueden mostrar capas meteorológicas.")
        
        # Añadir marcador de ubicación actual
        folium.Marker(
            location=[st.session_state.lat, st.session_state.lon],
            popup=f"Ubicación actual\nLat: {st.session_state.lat:.4f}\nLon: {st.session_state.lon:.4f}",
            icon=folium.Icon(color="red", icon="map-pin", prefix="fa")
        ).add_to(m)
        
        # Añadir marcador si ya se ha hecho clic en el mapa
        if "last_clicked" in st.session_state:
            clicked_lat = st.session_state.last_clicked["lat"]
            clicked_lon = st.session_state.last_clicked["lng"]
            
            folium.Marker(
                location=[clicked_lat, clicked_lon],
                popup=f"Nueva ubicación\nLat: {clicked_lat:.4f}\nLon: {clicked_lon:.4f}",
                icon=folium.Icon(color="blue", icon="cloud", prefix="fa")
            ).add_to(m)
        
        # Añadir control de capas
        folium.LayerControl().add_to(m)
        
        # Mostrar el mapa y manejar los clics
        map_data = st_folium(m, width=700, height=500)
        
        # Manejar clicks en el mapa
        if map_data and map_data.get("last_clicked"):
            new_lat = map_data["last_clicked"]["lat"]
            new_lon = map_data["last_clicked"]["lng"]
            
            # Actualizar la ubicación si ha cambiado
            if abs(new_lat - st.session_state.lat) > 0.0001 or abs(new_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat = new_lat
                st.session_state.lon = new_lon
                st.session_state.last_clicked = {"lat": new_lat, "lng": new_lon}
                st.success(f"📍 Nueva ubicación seleccionada: {new_lat:.4f}, {new_lon:.4f}")
                st.rerun()
        
        # Mostrar información adicional sobre las capas
        with st.expander("ℹ️ Información sobre las capas meteorológicas"):
            st.markdown("""
            **Capas meteorológicas disponibles de OpenWeatherMap:**
            
            - **🌧️ Precipitación**: Visualiza la intensidad de lluvia y precipitación en tiempo real
            - **☁️ Nubosidad**: Muestra la cobertura de nubes y su densidad
            - **🌡️ Temperatura**: Presenta la distribución de temperaturas en la región
            - **💨 Presión**: Indica la presión atmosférica con diferentes colores
            - **💨 Viento**: Muestra vectores de velocidad y dirección del viento
              **Nota**: Las capas meteorológicas se actualizan cada 10 minutos y requieren una 
            conexión activa a internet. Los datos son proporcionados gratuitamente por OpenWeatherMap.
            """)
            
            if config.OPENWEATHER_API_KEY:
                st.success("✅ API Key configurada correctamente")
            else:
                st.error("❌ API Key no configurada. Configure OPENWEATHER_API_KEY en el archivo .env")
                
    def _obtener_y_procesar_datos(self):
        """
        Obtiene datos climáticos, procesa y muestra resultados y visualizaciones.
        """        
        # Si se están usando datos personalizados
        if st.session_state.use_custom_data:
            st.info("Procesando datos meteorológicos personalizados")
            
            # Crear un diccionario con los datos personalizados
            datos_procesados = {
                'temperature': st.session_state.custom_temp,
                'dew_point': st.session_state.custom_dew_point,
                'pressure': st.session_state.custom_pressure,
                'humidity': st.session_state.custom_humidity,
                'wind_speed': st.session_state.custom_wind_speed,
                'wind_direction': st.session_state.custom_wind_direction,
                'lat': st.session_state.lat,
                'lon': st.session_state.lon
            }
            
            # Preparar array para el modelo con todos los campos requeridos
            input_data = np.array([[
                pd.Timestamp.now().timestamp(), 
                st.session_state.lat, 
                st.session_state.lon, 
                4.87,  # Elevación estimada
                st.session_state.custom_wind_direction,
                st.session_state.custom_wind_speed, 
                22000,  # Altura de techo (valor por defecto) 
                16093,  # Visibilidad (valor por defecto)
                st.session_state.custom_temp,
                st.session_state.custom_dew_point,
                st.session_state.custom_pressure
            ]])
            
            # Aplicar normalización
            input_scaled = self.predictor.scaler.transform(input_data)
            
            # Reformatear para LSTM
            input_lstm = np.reshape(input_scaled, (1, 1, input_scaled.shape[1]))
            
            # Mostrar datos y hacer predicción
            self._mostrar_datos_actuales(datos_procesados)
            prob = self.predictor.predecir(input_lstm)
            self._mostrar_resultado_prediccion(prob)
            
            # Mostrar visualizaciones primero
            self._mostrar_visualizaciones(datos_procesados, prob, input_lstm)
            
            # Generar y mostrar análisis LLM después
            self._mostrar_analisis_llm(datos_procesados, prob)
            
            return
            
        # Si se están usando datos en tiempo real
        with st.spinner(f"Obteniendo datos climáticos para lat={st.session_state.lat}, lon={st.session_state.lon}"):
            # Obtener datos climáticos actuales
            datos_climaticos = self.api_client.obtener_datos_actuales(st.session_state.lat, st.session_state.lon)
            
            if not datos_climaticos or "main" not in datos_climaticos:
                st.warning("No se pudo obtener información climática de la API. Intentando usar datos históricos de la base de datos.")
                # Intentar obtener y mostrar datos históricos de la BD
                df_hist = self.data_processor.obtener_datos_historicos_bd(
                    st.session_state.lat,
                    st.session_state.lon,
                    limit=1  # Solo necesitamos el más reciente para la predicción
                )
                
                if df_hist is not None and not df_hist.empty:
                    st.success("Se encontraron datos históricos para esta ubicación.")
                    
                    # Obtener la primera fila (más reciente) para la predicción
                    ultima_fila = df_hist.iloc[0]
                    
                    # Crear un diccionario con los datos procesados
                    datos_procesados = {
                        'temperature': ultima_fila.get('Temperatura', 0),
                        'dew_point': ultima_fila.get('Punto_Rocio', 0),
                        'pressure': ultima_fila.get('Presion', 1010),
                        'humidity': 70,  # Estimación, ya que no está en los datos originales
                        'wind_speed': ultima_fila.get('Viento', 0),
                        'wind_direction': 0,  # Valor por defecto
                        'lat': st.session_state.lat,
                        'lon': st.session_state.lon
                    }
                    
                    # Preparar array para el modelo con todos los campos requeridos
                    input_data = np.array([[
                        pd.Timestamp.now().timestamp(), 
                        st.session_state.lat,
                        st.session_state.lon,
                        4.87,  # Elevación estimada
                        0,  # Dirección del viento (valor por defecto)
                        ultima_fila.get('Viento', 0), 
                        22000,  # Altura de techo (valor por defecto) 
                        16093,  # Visibilidad (valor por defecto)
                        ultima_fila.get('Temperatura', 0),
                        ultima_fila.get('Punto_Rocio', 0),
                        ultima_fila.get('Presion', 1010)
                    ]])
                    
                    # Aplicar normalización
                    input_scaled = self.predictor.scaler.transform(input_data)
                    
                    # Reformatear para LSTM
                    input_lstm = np.reshape(input_scaled, (1, 1, input_scaled.shape[1]))                    
                    
                    # Mostrar datos y hacer predicción
                    self._mostrar_datos_actuales(datos_procesados)
                    prob = self.predictor.predecir(input_lstm)
                    self._mostrar_resultado_prediccion(prob)
                    
                    # Mostrar visualizaciones primero
                    self._mostrar_visualizaciones(datos_procesados, prob, input_lstm)
                    
                    # Generar y mostrar análisis LLM después
                    self._mostrar_analisis_llm(datos_procesados, prob)
                    
                    # Finalizar la función aquí
                    return
                else:
                    st.error("No se pudo obtener información climática para la ubicación seleccionada.")
                    return
                
            # Procesar datos para el modelo
            datos_procesados, input_lstm = self.data_processor.procesar_datos_actuales(
                datos_climaticos, 
                st.session_state.lat, 
                st.session_state.lon
            )
            
            # Hacer predicción
            prob = self.predictor.predecir(input_lstm)              
            
            # Mostrar datos y resultados
            self._mostrar_datos_actuales(datos_procesados)
            self._mostrar_resultado_prediccion(prob)
            
            # Mostrar visualizaciones primero
            self._mostrar_visualizaciones(datos_procesados, prob, input_lstm)
            
            # Generar y mostrar análisis LLM después
            self._mostrar_analisis_llm(datos_procesados, prob)
    
    def _mostrar_datos_actuales(self, datos):
        """
        Muestra los datos meteorológicos actuales.
        
        Args:
            datos (dict): Diccionario con los datos procesados.
        """
        st.subheader("Datos Meteorológicos Actuales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Temperatura:** {datos.get('temperature', 0)}°C")
            st.write(f"**Punto de Rocío:** {datos.get('dew_point', 0):.2f}°C")
            st.write(f"**Presión Atmosférica:** {datos.get('pressure', 0)} hPa")
            
        with col2:
            st.write(f"**Humedad Relativa:** {datos.get('humidity', 0)}%")
            st.write(f"**Velocidad del Viento:** {datos.get('wind_speed', 0)} m/s")
            st.write(f"**Dirección del Viento:** {datos.get('wind_direction', 0)}°")
    
    def _mostrar_resultado_prediccion(self, prob):
        """
        Muestra el resultado de la predicción de lluvia.
        
        Args:
            prob (float): Probabilidad de lluvia (0-1).
        """
        st.subheader("Resultado de la Predicción")
        
        # Convertir probabilidad a porcentaje
        prob_percent = prob * 100
        
        # Determinar el color según la probabilidad
        if prob_percent < 30:
            color = "green"
        elif prob_percent < 70:
            color = "orange"
        else:
            color = "red"
            
        # Mostrar resultado
        st.markdown(
            f"<h1 style='text-align: center; color: {color};'>Probabilidad de lluvia: {prob_percent:.2f}%</h1>", 
            unsafe_allow_html=True
        )
    
    def _obtener_datos_historicos_para_visualizacion(self, current_weather_data: Dict[str, Any]) -> pd.DataFrame | None:
        """
        Obtiene datos históricos desde múltiples fuentes para las visualizaciones.
        """
        df_hist = None
        
        # 1. Intentar obtener desde la API (si está definido en la clase WeatherAPIClient)
        try:
            df_hist = self.api_client.obtener_datos_historicos(
                lat=st.session_state.lat,
                lon=st.session_state.lon,
                dias=5
            )
            if df_hist is not None and not df_hist.empty:
                st.success("Datos históricos obtenidos de la API de OpenWeatherMap")
        except Exception as e:
            st.info("No se pudieron obtener datos históricos de la API. Intentando con la base de datos local...")
            
        # 2. Si no hay datos de la API, intentar con la base de datos
        if df_hist is None or df_hist.empty:
            try:
                df_hist = self.data_processor.obtener_datos_historicos_bd(
                    lat=st.session_state.lat,
                    lon=st.session_state.lon,
                    limit=30
                )
                if df_hist is not None and not df_hist.empty:
                    st.success("Datos históricos obtenidos de la base de datos")
                else:
                    st.warning("No se encontraron datos históricos en la base de datos para esta ubicación")
            except Exception as e:
                st.error(f"Error al obtener datos históricos de la BD: {e}")
        
        # 3. Si no hay datos de ninguna fuente, generar simulados
        if df_hist is None or df_hist.empty:
            st.warning("No se pudieron obtener datos históricos reales. Mostrando datos simulados.")
            df_hist = self.data_processor.generar_datos_ejemplo(current_weather_data)
        
        return df_hist
    
    def _mostrar_visualizaciones(self, datos, prob, input_lstm=None):
        """
        Muestra diversas visualizaciones de los datos meteorológicos.
        
        Args:
            datos (dict): Diccionario con los datos procesados.
            prob (float): Probabilidad de lluvia.
            input_lstm (numpy.ndarray, optional): Datos de entrada formateados para LSTM.
        """
        st.header("Visualizaciones")
        
        # Crear pestañas para las diferentes visualizaciones
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Gráfico de Radar", 
            "Gráfico de Barras", 
            "Indicador de Probabilidad",
            "Datos Históricos", 
            "Diagrama de Dispersión"
        ])
        
        # Tab 1: Gráfico de Radar
        with tab1:
            st.subheader("Gráfico de Radar de Variables Meteorológicas")
            
            # Preparar datos para el gráfico de radar
            variables = ['Temperatura', 'Humedad', 'Punto de Rocío', 'Velocidad del Viento', 'Presión']
            valores = [
                datos.get('temperature', 0), 
                datos.get('humidity', 0), 
                datos.get('dew_point', 0), 
                datos.get('wind_speed', 0), 
                datos.get('pressure', 0)/10  # Escalar la presión para mejor visualización
            ]
            
            # Valores de referencia para comparación
            valores_lluvia = [22, 80, 18, 5, 101]  # Valores hipotéticos para días de lluvia
            
            # Crear y mostrar el gráfico
            fig = self.visualizer.plot_radar_chart(valores, variables, valores_lluvia)
            st.plotly_chart(fig)
            
        # Tab 2: Gráfico de Barras
        with tab2:
            st.subheader("Comparación de Variables Meteorológicas")
            
            # Preparar datos para el gráfico de barras
            variables_barras = ['Temperatura', 'Humedad', 'Punto de Rocío', 'Velocidad del Viento']
            valores_barras = [
                datos.get('temperature', 0), 
                datos.get('humidity', 0), 
                datos.get('dew_point', 0), 
                datos.get('wind_speed', 0)
            ]
            
            # Colores para las barras
            colores = ['#72B7B2', '#DA8137', '#54A24B', '#4C78A8']
            
            # Crear y mostrar el gráfico
            fig = self.visualizer.plot_bar_chart(valores_barras, variables_barras, colores)
            st.pyplot(fig)
            
        # Tab 3: Indicador de Probabilidad
        with tab3:
            st.subheader("Indicador de Probabilidad de Lluvia")
            
            # Crear y mostrar el indicador
            fig = self.visualizer.plot_gauge(
                prob * 100, 
                titulo="Probabilidad de lluvia (%)"
            )
            st.plotly_chart(fig)
        
        # Obtener datos históricos usando el nuevo método
        df_hist = self._obtener_datos_historicos_para_visualizacion(datos)

        # Tab 4: Datos Históricos
        with tab4:
            st.subheader("Datos Históricos")
            
            if df_hist is not None and not df_hist.empty:
                # Graficar datos históricos
                if "Humedad" in df_hist.columns:
                    st.line_chart(df_hist[["Temperatura", "Humedad"]])
                else:
                    # Si no hay columna de humedad, mostrar solo temperatura
                    st.line_chart(df_hist[["Temperatura"]])
                
                # Mostrar probabilidad de lluvia si está disponible
                if "Probabilidad_Lluvia" in df_hist.columns:
                    st.subheader("Lluvia histórica")
                    st.line_chart(df_hist[["Probabilidad_Lluvia"]])
                
                # Mostrar tabla de datos
                st.write("Datos históricos:")
                st.dataframe(df_hist)
            else:
                st.warning("No hay datos históricos disponibles para mostrar.")
            
        # Tab 5: Diagrama de Dispersión
        with tab5:
            st.subheader("Diagrama de Dispersión de Datos Históricos")
            
            # Crear y mostrar diagrama de dispersión de datos históricos
            if df_hist is not None and not df_hist.empty and 'Probabilidad_Lluvia' in df_hist.columns:
                fig = self.visualizer.plot_scatter(
                    df_hist, 
                    'Temperatura', 
                    'Probabilidad_Lluvia',
                    hue_col='Probabilidad_Lluvia'
                )
                st.pyplot(fig)
            else:
                st.warning("No hay suficientes datos para generar el Diagrama (requiere 'Probabilidad_Lluvia').")
        
        # Información de depuración si es necesario
        with st.expander("Información de depuración"):
            if input_lstm is not None:
                st.write(f"**Debug:** Input Shape = {input_lstm.shape}, Prediction = {prob}")
            else:
                st.write(f"**Debug:** Prediction = {prob}")
    
    def _mostrar_analisis_llm(self, datos: Dict[str, Any], prob: float):
        """
        Muestra el análisis generado por el LLM basado en la predicción del LSTM.
        
        Args:
            datos (dict): Diccionario con los datos procesados.
            prob (float): Probabilidad de lluvia (0-1).
        """
        st.header("🤖 Análisis Inteligente")
        
        # Verificar si el LLM client está disponible
        if not self.llm_client:
            st.warning("⚠️ Cliente LLM no disponible. Mostrando análisis básico.")
            self._mostrar_analisis_basico(datos, prob)
            return
        
        # Verificar conexión con LM Studio
        with st.spinner("Conectando con el modelo de lenguaje..."):
            conexion_ok = self.llm_client.test_conexion()
        
        if conexion_ok:
            st.success("✅ Conectado a LM Studio")
            
            # Crear tabs para diferentes tipos de análisis
            tab_analisis, tab_reporte = st.tabs([
                "📊 Análisis de Predicción", 
                "📋 Reporte Completo"
            ])
            
            with tab_analisis:
                st.subheader("Análisis de la Predicción de Lluvia")
                
                with st.spinner("Generando análisis inteligente..."):
                    analisis = self.llm_client.generar_analisis_prediccion(datos, prob)
                
                st.markdown(analisis)
                
                # Botón para regenerar análisis
                if st.button("🔄 Regenerar análisis", key="regenerar_analisis"):
                    with st.spinner("Regenerando análisis..."):
                        analisis = self.llm_client.generar_analisis_prediccion(datos, prob)
                    st.markdown(analisis)
            
            with tab_reporte:
                st.subheader("Reporte Meteorológico Completo")
                
                ubicacion = {
                    'lat': st.session_state.lat,
                    'lon': st.session_state.lon
                }
                
                with st.spinner("Generando reporte completo..."):
                    reporte = self.llm_client.generar_reporte_completo(datos, prob, ubicacion)
                
                st.markdown(reporte)
                
                # Botón para descargar reporte
                st.download_button(
                    label="💾 Descargar reporte",
                    data=reporte,
                    file_name=f"reporte_meteorologico_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
        else:
            st.warning("⚠️ LM Studio no disponible. Mostrando análisis básico.")
            self._mostrar_analisis_basico(datos, prob)
    
    def _mostrar_analisis_basico(self, datos: Dict[str, Any], prob: float):
        """
        Muestra un análisis básico cuando el LLM no está disponible.
        
        Args:
            datos (dict): Diccionario con los datos procesados.
            prob (float): Probabilidad de lluvia (0-1).
        """
        prob_percent = prob * 100
        
        st.subheader("Análisis Básico de Predicción")
        
        # Determinar nivel de probabilidad
        if prob_percent < 30:
            nivel = "🟢 BAJA"
            descripcion = "Las condiciones meteorológicas actuales indican una baja probabilidad de lluvia."
            recomendacion = "✅ Condiciones favorables para actividades al aire libre."
        elif prob_percent < 70:
            nivel = "🟡 MODERADA"
            descripcion = "Las condiciones meteorológicas muestran una probabilidad moderada de lluvia."
            recomendacion = "☂️ Se recomienda llevar paraguas como precaución."
        else:
            nivel = "🔴 ALTA"
            descripcion = "Las condiciones meteorológicas indican alta probabilidad de lluvia."
            recomendacion = "🌧️ Se recomienda reprogramar actividades al aire libre."
        
        # Mostrar análisis
        st.markdown(f"""
        **Probabilidad de Lluvia: {prob_percent:.1f}% - {nivel}**
        
        {descripcion}
        
        **Condiciones Actuales:**
        - 🌡️ **Temperatura:** {datos.get('temperature', 'N/A')}°C
        - 💧 **Humedad:** {datos.get('humidity', 'N/A')}%
        - 🌡️ **Punto de Rocío:** {datos.get('dew_point', 'N/A')}°C
        - 📊 **Presión:** {datos.get('pressure', 'N/A')} hPa
        - 💨 **Viento:** {datos.get('wind_speed', 'N/A')} m/s
        
        **Recomendación:** {recomendacion}
        
        ---
        *Análisis generado localmente por el modelo LSTM. Para análisis más detallado, conecte LM Studio.*
        """)
        
        # Información adicional
        with st.expander("ℹ️ Información adicional"):
            humidity = datos.get('humidity', 0)
            if humidity > 70:
                humidity_level = 'alta'
            elif humidity > 40:
                humidity_level = 'moderada'
            else:
                humidity_level = 'baja'

            temperature = datos.get('temperature', 0)
            if temperature > 25:
                temperature_level = 'cálida'
            elif temperature > 15:
                temperature_level = 'templada'
            else:
                temperature_level = 'fresca'

            pressure = datos.get('pressure', 0)
            if pressure > 1015:
                pressure_level = 'alta'
            elif pressure > 1000:
                pressure_level = 'normal'
            else:
                pressure_level = 'baja'
            
            st.markdown(f"""
            **Sobre la Predicción:**
            - Modelo utilizado: LSTM (Long Short-Term Memory)
            - Datos de entrada: Variables meteorológicas actuales
            - Precisión del modelo: Basado en datos históricos locales
            
            **Factores Clave:**
            - La humedad relativa del {datos.get('humidity', 'N/A')}% es {humidity_level}
            - La temperatura de {datos.get('temperature', 'N/A')}°C es {temperature_level}
            - La presión atmosférica de {datos.get('pressure', 'N/A')} hPa está {pressure_level}
            """)

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()