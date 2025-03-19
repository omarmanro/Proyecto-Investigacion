import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import requests
import folium
from streamlit_folium import st_folium

# API Key de OpenWeatherMap
API_KEY = "e63d503e181ce2fd667ad05b4aaed60c"

# Cargar el modelo entrenado y el scaler
@st.cache_resource
def cargar_modelo_y_scaler():
    modelo = tf.keras.models.load_model('../modelo_lluvia_lstm.h5')
    scaler = joblib.load('../scaler_lstm.pkl')
    return modelo, scaler

modelo, scaler = cargar_modelo_y_scaler()

# Obtener datos climáticos desde OpenWeatherMap
def obtener_datos_climaticos(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al llamar a la API: {response.status_code} - {response.text}")
        return None

# Calcular punto de rocío
def calcular_punto_rocio(temperatura, humedad_relativa):
    return temperatura - ((100 - humedad_relativa) / 5)

# Inicializar valores en session_state
if "lat" not in st.session_state:
    st.session_state.lat = 25.685194
if "lon" not in st.session_state:
    st.session_state.lon = -109.080806

# Panel lateral para seleccionar coordenadas
st.sidebar.header("Ubicación geográfica")
lat = st.sidebar.number_input("Latitud", value=st.session_state.lat, format="%.6f", key="lat_input")
lon = st.sidebar.number_input("Longitud", value=st.session_state.lon, format="%.6f", key="lon_input")

# Mostrar el mapa para elegir ubicación con folium
def seleccionar_ubicacion():
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=10)
    m.add_child(folium.LatLngPopup())
    
    if "last_clicked" in st.session_state:
        folium.Marker(
            location=[st.session_state.last_clicked["lat"], st.session_state.last_clicked["lng"]],
            icon=folium.Icon(color="blue", icon="cloud")  # Use a simple cloud icon
        ).add_to(m)
    
    map_data = st_folium(m, width=700, height=500)
    
    if map_data and map_data.get("last_clicked"):
        new_lat = map_data["last_clicked"]["lat"]
        new_lon = map_data["last_clicked"]["lng"]
        
        if new_lat != st.session_state.lat or new_lon != st.session_state.lon:
            st.session_state.lat = new_lat
            st.session_state.lon = new_lon
            st.session_state.last_clicked = {"lat": new_lat, "lng": new_lon}
            st.rerun()
        
    return map_data

seleccionar_ubicacion()

# Obtener datos en tiempo real
if st.sidebar.button("Obtener datos climáticos en tiempo real"):
    with st.spinner(f"Obteniendo datos climáticos para lat={st.session_state.lat}, lon={st.session_state.lon}"):
        datos_climaticos = obtener_datos_climaticos(st.session_state.lat, st.session_state.lon)
    
    if datos_climaticos and "main" in datos_climaticos:
        temp = datos_climaticos['main']['temp']
        humedad = datos_climaticos['main']['humidity']
        dew = calcular_punto_rocio(temp, humedad)
        elevation = 4.87  # Estimado, ajustable
        wnd_direction = datos_climaticos.get('wind', {}).get('deg', 0)
        wnd_speed = datos_climaticos.get('wind', {}).get('speed', 0)
        cig_height = 22000  # No disponible en OpenWeatherMap
        vis_distance = datos_climaticos.get('visibility', 10000)  # Default a 10km si falta
        slp = datos_climaticos['main']['pressure']
        date = pd.Timestamp.now().timestamp()  # Añadir la fecha actual como timestamp

        # Mostrar datos obtenidos
        st.write(f"**Temperatura:** {temp}°C")
        st.write(f"**Humedad Relativa:** {humedad}%")
        st.write(f"**Punto de Rocío:** {dew:.2f}°C")
        st.write(f"**Dirección del Viento:** {wnd_direction}°")
        st.write(f"**Velocidad del Viento:** {wnd_speed} m/s")
        st.write(f"**Visibilidad:** {vis_distance} m")
        st.write(f"**Presión Atmosférica:** {slp} hPa")

        # Preparar datos para la predicción
        input_data = np.array([[date, st.session_state.lat, st.session_state.lon, elevation, 
                                wnd_direction, wnd_speed, cig_height, vis_distance, 
                                temp, dew, slp]])

        input_scaled = scaler.transform(input_data)
        input_lstm = np.reshape(input_scaled, (1, 1, input_scaled.shape[1]))  # Reshape para LSTM

        # Hacer la predicción
        prob = modelo.predict(input_lstm)[0][0]

        # Mostrar el resultado
        st.success(f"Probabilidad de lluvia/tormenta: {prob * 100:.2f}%")

        # Debugging
        st.write(f"**Debug:** Input Shape = {input_lstm.shape}, Prediction = {prob}")

    else:
        st.error("No se pudo obtener información climática para la ubicación seleccionada.")
