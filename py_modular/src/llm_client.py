"""
Cliente para interactuar con LM Studio para generar análisis de predicciones meteorológicas.
"""
import requests
import json
from typing import Dict, Any, Optional
from .config import config

class LLMClient:
    """
    Cliente para comunicarse con LM Studio y generar análisis de predicciones meteorológicas.
    """
    
    def __init__(self):
        """
        Inicializa el cliente LLM con la configuración de LM Studio.
        """
        self.api_url = config.LLM_API_URL
        self.model_name = config.LLM_MODEL_NAME
        self.max_tokens = config.LLM_MAX_TOKENS
        self.temperature = config.LLM_TEMPERATURE
        
    def _hacer_peticion(self, prompt: str) -> Optional[str]:
        """
        Hace una petición al LLM de LM Studio.
        
        Args:
            prompt (str): El prompt para enviar al LLM.
            
        Returns:
            Optional[str]: La respuesta del LLM o None si hay error.
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer not-needed'  # Required by the API even if not used
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un experto meteorólogo que analiza datos climáticos y predicciones de lluvia. Proporciona análisis claros, precisos y útiles para usuarios no técnicos."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=90
            )
            
            if response.status_code == 200:
                response_json = response.json()
                return response_json['choices'][0]['message']['content']
            else:
                print(f"Error en petición LLM: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error al conectar con LM Studio: {e}")
            return None
    
    def generar_analisis_prediccion(self, datos_meteorologicos: Dict[str, Any], probabilidad_lluvia: float) -> str:
        """
        Genera un análisis en lenguaje natural de la predicción de lluvia.
        
        Args:
            datos_meteorologicos (Dict): Datos meteorológicos actuales.
            probabilidad_lluvia (float): Probabilidad de lluvia (0-1).
            
        Returns:
            str: Análisis en lenguaje natural.
        """
        prob_percent = probabilidad_lluvia * 100
        
        prompt = f"""
        Analiza la siguiente información meteorológica y proporciona un análisis detallado en español:

        DATOS METEOROLÓGICOS ACTUALES:
        - Temperatura: {datos_meteorologicos.get('temperature', 'N/A')}°C
        - Humedad: {datos_meteorologicos.get('humidity', 'N/A')}%
        - Punto de rocío: {datos_meteorologicos.get('dew_point', 'N/A')}°C
        - Presión atmosférica: {datos_meteorologicos.get('pressure', 'N/A')} hPa
        - Velocidad del viento: {datos_meteorologicos.get('wind_speed', 'N/A')} m/s
        - Dirección del viento: {datos_meteorologicos.get('wind_direction', 'N/A')}°

        PREDICCIÓN DEL MODELO LSTM:
        - Probabilidad de lluvia: {prob_percent:.2f}%

        Por favor, proporciona:
        1. Una interpretación clara de la probabilidad de lluvia
        2. Análisis de las condiciones meteorológicas actuales
        3. Explicación de cómo estos factores influyen en la predicción
        4. Recomendaciones prácticas para el usuario
        5. Nivel de confianza en la predicción

        Mantén el análisis conciso pero informativo, dirigido a usuarios no técnicos.
        """
        
        respuesta = self._hacer_peticion(prompt)
        
        if respuesta:
            return respuesta
        else:
            return self._generar_analisis_fallback(datos_meteorologicos, probabilidad_lluvia)
    
    def explicar_graficas(self, tipo_grafica: str, datos_meteorologicos: Dict[str, Any], probabilidad_lluvia: float) -> str:
        """
        Genera explicaciones para las diferentes gráficas mostradas en la aplicación.
        
        Args:
            tipo_grafica (str): Tipo de gráfica ('radar', 'barras', 'gauge', 'historicos', 'dispersion').
            datos_meteorologicos (Dict): Datos meteorológicos actuales.
            probabilidad_lluvia (float): Probabilidad de lluvia (0-1).
            
        Returns:
            str: Explicación de la gráfica.
        """
        prob_percent = probabilidad_lluvia * 100
        
        explicaciones_base = {
            'radar': f"""
            El gráfico de radar muestra las variables meteorológicas actuales comparadas con condiciones típicas de lluvia.
            
            Variables actuales:
            - Temperatura: {datos_meteorologicos.get('temperature', 'N/A')}°C
            - Humedad: {datos_meteorologicos.get('humidity', 'N/A')}%
            - Punto de rocío: {datos_meteorologicos.get('dew_point', 'N/A')}°C
            - Velocidad del viento: {datos_meteorologicos.get('wind_speed', 'N/A')} m/s
            """,
            
            'barras': f"""
            El gráfico de barras compara las principales variables meteorológicas actuales.
            Estas variables son clave para determinar la probabilidad de lluvia del {prob_percent:.1f}%.
            """,
            
            'gauge': f"""
            El indicador circular muestra la probabilidad de lluvia: {prob_percent:.1f}%.
            - Verde (0-30%): Baja probabilidad
            - Amarillo (30-70%): Probabilidad moderada  
            - Rojo (70-100%): Alta probabilidad
            """,
            
            'historicos': """
            Los datos históricos muestran las tendencias meteorológicas recientes en la ubicación seleccionada.
            Estos patrones ayudan a contextualizar la predicción actual.
            """,
            
            'dispersion': f"""
            El diagrama de dispersión relaciona la temperatura con la probabilidad histórica de lluvia,
            ayudando a entender patrones en los datos para la predicción actual del {prob_percent:.1f}%.
            """
        }
        
        prompt = f"""
        Explica de manera clara y educativa el siguiente tipo de gráfica meteorológica:

        TIPO DE GRÁFICA: {tipo_grafica.upper()}
        
        CONTEXTO ACTUAL:
        {explicaciones_base.get(tipo_grafica, 'Gráfica meteorológica')}
        
        Probabilidad de lluvia actual: {prob_percent:.2f}%
        
        Por favor explica:
        1. Qué muestra esta gráfica específicamente
        2. Cómo interpretar la información presentada
        3. Qué patrones o tendencias son importantes observar
        4. Cómo se relaciona con la predicción de lluvia actual
        
        Usa lenguaje claro y accesible para usuarios no técnicos.
        """
        
        respuesta = self._hacer_peticion(prompt)
        
        if respuesta:
            return respuesta
        else:
            return explicaciones_base.get(tipo_grafica, "Explicación no disponible en este momento.")
    
    def generar_reporte_completo(self, datos_meteorologicos: Dict[str, Any], probabilidad_lluvia: float, ubicacion: Dict[str, float]) -> str:
        """
        Genera un reporte meteorológico completo.
        
        Args:
            datos_meteorologicos (Dict): Datos meteorológicos actuales.
            probabilidad_lluvia (float): Probabilidad de lluvia (0-1).
            ubicacion (Dict): Coordenadas de latitud y longitud.
            
        Returns:
            str: Reporte meteorológico completo.
        """
        prob_percent = probabilidad_lluvia * 100
        
        prompt = f"""
        Genera un reporte meteorológico completo y profesional en español para la ubicación:
        Latitud: {ubicacion.get('lat', 'N/A')}, Longitud: {ubicacion.get('lon', 'N/A')}

        DATOS METEOROLÓGICOS ACTUALES:
        - Temperatura: {datos_meteorologicos.get('temperature', 'N/A')}°C
        - Humedad relativa: {datos_meteorologicos.get('humidity', 'N/A')}%
        - Punto de rocío: {datos_meteorologicos.get('dew_point', 'N/A')}°C
        - Presión atmosférica: {datos_meteorologicos.get('pressure', 'N/A')} hPa
        - Velocidad del viento: {datos_meteorologicos.get('wind_speed', 'N/A')} m/s
        - Dirección del viento: {datos_meteorologicos.get('wind_direction', 'N/A')}°

        PREDICCIÓN IA (LSTM):
        - Probabilidad de lluvia: {prob_percent:.2f}%

        El reporte debe incluir:
        1. **Resumen ejecutivo** de las condiciones actuales
        2. **Análisis detallado** de cada variable meteorológica
        3. **Interpretación de la predicción** del modelo de IA
        4. **Factores climáticos** que influyen en el pronóstico
        5. **Recomendaciones prácticas** para actividades al aire libre
        6. **Nivel de confianza** en la predicción
        7. **Contexto estacional** si es relevante

        Estructura el reporte de manera profesional y accesible.
        """
        
        respuesta = self._hacer_peticion(prompt)
        
        if respuesta:
            return respuesta
        else:
            return self._generar_reporte_fallback(datos_meteorologicos, probabilidad_lluvia, ubicacion)
    
    def _generar_analisis_fallback(self, datos_meteorologicos: Dict[str, Any], probabilidad_lluvia: float) -> str:
        """
        Genera un análisis básico cuando el LLM no está disponible.
        """
        prob_percent = probabilidad_lluvia * 100
        
        if prob_percent < 30:
            nivel = "baja"
            recomendacion = "Condiciones favorables para actividades al aire libre."
        elif prob_percent < 70:
            nivel = "moderada"
            recomendacion = "Se recomienda llevar paraguas como precaución."
        else:
            nivel = "alta"
            recomendacion = "Alta probabilidad de lluvia. Se recomienda reprogramar actividades al aire libre."
        
        return f"""
        **Análisis de Predicción Meteorológica**
        
        La probabilidad de lluvia es del {prob_percent:.1f}%, lo que indica una probabilidad {nivel}.
        
        **Condiciones actuales:**
        - Temperatura: {datos_meteorologicos.get('temperature', 'N/A')}°C
        - Humedad: {datos_meteorologicos.get('humidity', 'N/A')}%
        - Presión: {datos_meteorologicos.get('pressure', 'N/A')} hPa
        
        **Recomendación:** {recomendacion}
        
        *Nota: Análisis generado localmente. Servicio LLM no disponible.*
        """
    
    def _generar_reporte_fallback(self, datos_meteorologicos: Dict[str, Any], probabilidad_lluvia: float, ubicacion: Dict[str, float]) -> str:
        """
        Genera un reporte básico cuando el LLM no está disponible.
        """
        prob_percent = probabilidad_lluvia * 100
        
        return f"""
        **REPORTE METEOROLÓGICO**
        
        **Ubicación:** Lat: {ubicacion.get('lat', 'N/A')}, Lon: {ubicacion.get('lon', 'N/A')}
        
        **Condiciones Actuales:**
        - Temperatura: {datos_meteorologicos.get('temperature', 'N/A')}°C
        - Humedad Relativa: {datos_meteorologicos.get('humidity', 'N/A')}%
        - Punto de Rocío: {datos_meteorologicos.get('dew_point', 'N/A')}°C
        - Presión Atmosférica: {datos_meteorologicos.get('pressure', 'N/A')} hPa
        - Viento: {datos_meteorologicos.get('wind_speed', 'N/A')} m/s
        
        **Predicción de Lluvia:** {prob_percent:.1f}%
        
        **Análisis:** Predicción generada por modelo LSTM entrenado con datos históricos.
        
        *Nota: Reporte básico generado localmente. Servicio LLM no disponible.*
        """    
    def test_conexion(self) -> bool:
        """
        Prueba la conexión con el servidor LM Studio.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            headers = {
                'Authorization': 'Bearer not-needed'  # Required by the API even if not used
            }
            response = requests.get(
                f"{self.api_url}/models", 
                headers=headers,
                timeout=10  # Aumentado de 5 a 10 segundos
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error al conectar con LM Studio: {e}")
            return False
