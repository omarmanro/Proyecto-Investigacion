"""
Aplicación principal de Streamlit que integra todas las funcionalidades.
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from weather_data_processor import WeatherDataProcessor
from weather_api_client import WeatherAPIClient
from rainfall_predictor import RainfallPredictor
from weather_visualizer import WeatherVisualizer

class StreamlitApp:
    """
    Clase principal que gestiona la aplicación de Streamlit y coordina
    todos los componentes.
    """
    
    def __init__(self):
        """
        Inicializa la aplicación y carga todos los componentes necesarios.
        """
        # Configurar clave API
        self.API_KEY = "e63d503e181ce2fd667ad05b4aaed60c"
        
        # Inicializar componentes
        self.predictor = self._inicializar_predictor()
        self.api_client = WeatherAPIClient(self.API_KEY)
        self.data_processor = WeatherDataProcessor(self.predictor.scaler)
        self.visualizer = WeatherVisualizer()
        
        # Inicializar estado de la sesión
        self._inicializar_session_state()
        
    def _inicializar_predictor(self):
        """
        Inicializa el predictor de lluvia cargando el modelo y el scaler.
        
        Returns:
            RainfallPredictor: Instancia del predictor.
        """        # Determinar las rutas a los archivos del modelo
        modelo_path = './modelo_lluvia_lstm.h5'
        scaler_path = './scaler_lstm.pkl'
        
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
            st.session_state.lat = 25.685194
        if "lon" not in st.session_state:
            st.session_state.lon = -109.080806
            
    def run(self):
        """
        Ejecuta la aplicación principal de Streamlit.
        """
        st.title("Predicción de Lluvia con IA")
        
        # Crear panel lateral para controles
        self._crear_sidebar()
        
        # Mostrar mapa para seleccionar ubicación
        self._mostrar_mapa_seleccion()
        
        # Procesar datos si se solicita
        if st.session_state.get('procesar_datos', False):
            self._obtener_y_procesar_datos()
            
    def _crear_sidebar(self):
        """
        Crea el panel lateral con controles para la aplicación.
        """
        st.sidebar.header("Ubicación geográfica")
        
        # Inputs para coordenadas
        lat = st.sidebar.number_input(
            "Latitud", 
            value=st.session_state.lat, 
            format="%.6f", 
            key="lat_input"
        )
        lon = st.sidebar.number_input(
            "Longitud", 
            value=st.session_state.lon, 
            format="%.6f", 
            key="lon_input"
        )
        
        # Botón para obtener datos
        if st.sidebar.button("Obtener datos climáticos en tiempo real"):
            st.session_state.procesar_datos = True
        else:
            st.session_state.procesar_datos = False
            
    def _mostrar_mapa_seleccion(self):
        """
        Muestra un mapa interactivo para seleccionar la ubicación.
        """
        st.subheader("Seleccione una ubicación en el mapa")
        
        # Crear mapa con folium
        m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=10)
        m.add_child(folium.LatLngPopup())
        
        # Añadir marcador si ya se ha hecho clic en el mapa
        if "last_clicked" in st.session_state:
            folium.Marker(
                location=[st.session_state.last_clicked["lat"], st.session_state.last_clicked["lng"]],
                icon=folium.Icon(color="blue", icon="cloud")
            ).add_to(m)
        
        # Mostrar el mapa y manejar los clics
        map_data = st_folium(m, width=700, height=500)
        
        if map_data and map_data.get("last_clicked"):
            new_lat = map_data["last_clicked"]["lat"]
            new_lon = map_data["last_clicked"]["lng"]
            
            # Actualizar la ubicación si ha cambiado
            if new_lat != st.session_state.lat or new_lon != st.session_state.lon:
                st.session_state.lat = new_lat
                st.session_state.lon = new_lon
                st.session_state.last_clicked = {"lat": new_lat, "lng": new_lon}
                st.rerun()
                
    def _obtener_y_procesar_datos(self):
        """
        Obtiene datos climáticos, procesa y muestra resultados y visualizaciones.
        """        
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
                    self._mostrar_visualizaciones(datos_procesados, prob, input_lstm)
                    
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
            
            # Mostrar visualizaciones
            self._mostrar_visualizaciones(datos_procesados, prob, input_lstm)
            
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
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Gráfico de Radar", 
            "Gráfico de Barras", 
            "Indicador de Probabilidad",
            "Datos Históricos", 
            "Mapa de Calor", 
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
              # Tab 4: Datos Históricos
        with tab4:
            st.subheader("Datos Históricos")
            
            # Obtener datos históricos desde diferentes fuentes
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
                df_hist = self.data_processor.generar_datos_ejemplo(datos)
            
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
            
        # Tab 5: Mapa de Calor
        with tab5:
            st.subheader("Mapa de Calor de Variables Meteorológicas")
            
            # Preparar datos para el mapa de calor
            variables_calor = {
                'Temperatura': datos.get('temperature', 0),
                'Humedad': datos.get('humidity', 0),
                'Punto de Rocío': datos.get('dew_point', 0),
                'Velocidad del Viento': datos.get('wind_speed', 0),
                'Presión': datos.get('pressure', 0)
            }
            
            # Crear y mostrar el mapa de calor
            fig = self.visualizer.plot_heatmap(variables_calor)
            st.pyplot(fig)
            
        # Tab 6: Diagrama de Dispersión
        with tab6:
            st.subheader("Diagrama de Dispersión")
            
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
                st.warning("No hay suficientes datos para generar el diagrama de dispersión.")
        
        # Información de depuración si es necesario
        with st.expander("Información de depuración"):
            if input_lstm is not None:
                st.write(f"**Debug:** Input Shape = {input_lstm.shape}, Prediction = {prob}")
            else:
                st.write(f"**Debug:** Prediction = {prob}")
