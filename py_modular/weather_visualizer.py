"""
Visualizador de datos climáticos que genera gráficos interactivos.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import roc_curve, auc

class WeatherVisualizer:
    """
    Clase para generar visualizaciones interactivas de datos meteorológicos,
    adaptada para su uso con Streamlit.
    """
    
    def __init__(self):
        """
        Inicializa el visualizador sin necesidad de parámetros adicionales.
        """
        pass
    
    def plot_radar_chart(self, valores, variables, valores_comparacion=None, titulo="Gráfico de Radar de Variables Meteorológicas"):
        """
        Genera un gráfico de radar (spider chart) para visualizar múltiples variables.
        
        Args:
            valores (list): Lista de valores para las variables.
            variables (list): Lista de nombres de las variables.
            valores_comparacion (list, optional): Lista de valores de referencia para comparación.
            titulo (str, optional): Título del gráfico.
            
        Returns:
            plotly.graph_objects.Figure: La figura creada.
        """
        fig = go.Figure()
        
        # Añadir los valores actuales
        fig.add_trace(go.Scatterpolar(
            r=valores,
            theta=variables,
            fill='toself',
            name='Valores Actuales'
        ))
        
        # Añadir valores de comparación si se proporcionan
        if valores_comparacion:
            fig.add_trace(go.Scatterpolar(
                r=valores_comparacion,
                theta=variables,
                fill='toself',
                name='Valores de Referencia'
            ))
        
        # Configurar el diseño
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            showlegend=True,
            title=titulo
        )
        
        return fig
        
    def plot_bar_chart(self, valores, variables, colores=None):
        """
        Genera un gráfico de barras para comparar variables.
        
        Args:
            valores (list): Lista de valores para las variables.
            variables (list): Lista de nombres de las variables.
            colores (list, optional): Lista de colores para las barras.
            
        Returns:
            matplotlib.figure.Figure: La figura creada.
        """
        # Crear DataFrame para el gráfico
        chart_data = pd.DataFrame({
            'Variable': variables,
            'Valor': valores
        })
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = sns.barplot(x='Variable', y='Valor', data=chart_data, ax=ax)
        
        # Personalizar el gráfico
        plt.title('Variables Meteorológicas Actuales')
        plt.ylabel('Valor')
        plt.grid(True, axis='y')
        
        # Aplicar colores si se proporcionan
        if colores:
            for i, bar in enumerate(bars.patches):
                bar.set_color(colores[i % len(colores)])
        
        return fig
        
    def plot_gauge(self, valor, titulo="Probabilidad", min_val=0, max_val=100):
        """
        Genera un indicador de aguja (gauge) para mostrar un valor en una escala.
        
        Args:
            valor (float): El valor a mostrar en el indicador.
            titulo (str, optional): Título del indicador.
            min_val (int, optional): Valor mínimo de la escala.
            max_val (int, optional): Valor máximo de la escala.
            
        Returns:
            plotly.graph_objects.Figure: La figura creada.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': titulo},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [min_val, max_val/3], 'color': "lightgreen"},
                    {'range': [max_val/3, 2*max_val/3], 'color': "orange"},
                    {'range': [2*max_val/3, max_val], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 2*max_val/3
                }
            }
        ))
        
        return fig
        
    def plot_time_series(self, df, columnas, titulo="Serie Temporal"):
        """
        Genera una gráfica de serie temporal para visualizar datos históricos.
        
        Args:
            df (pandas.DataFrame): DataFrame con datos históricos indexados por fecha.
            columnas (list): Lista de columnas a graficar.
            titulo (str, optional): Título del gráfico.
            
        Returns:
            matplotlib.figure.Figure: La figura creada.
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for columna in columnas:
            ax.plot(df.index, df[columna], label=columna)
        
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Valor')
        ax.set_title(titulo)
        ax.grid(True)
        ax.legend()
        
        plt.tight_layout()
        return fig
        
    def plot_scatter(self, df, x_col, y_col, hue_col=None, titulo=None):
        """
        Genera un diagrama de dispersión para mostrar relaciones entre variables.
        
        Args:
            df (pandas.DataFrame): DataFrame con los datos.
            x_col (str): Nombre de la columna para el eje X.
            y_col (str): Nombre de la columna para el eje Y.
            hue_col (str, optional): Nombre de la columna para colorear los puntos.
            titulo (str, optional): Título del gráfico.
            
        Returns:
            matplotlib.figure.Figure: La figura creada.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if hue_col and hue_col in df.columns:
            if df[hue_col].dtype == bool or (df[hue_col].dtype == 'object' and df[hue_col].nunique() <= 10):
                # Para variables categóricas
                sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
            else:
                # Para variables numéricas, aplicar un umbral y convertir a categórica
                umbral = df[hue_col].median()
                sns.scatterplot(data=df, x=x_col, y=y_col, 
                               hue=df[hue_col] > umbral, 
                               palette={True: 'red', False: 'blue'}, 
                               s=100, ax=ax)
        else:
            sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
        
        if not titulo:
            titulo = f'Diagrama de Dispersión: {x_col} vs {y_col}'
            
        ax.set_title(titulo)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True)
        
        return fig
        
    def plot_heatmap(self, valores, titulo="Mapa de Calor"):
        """
        Genera un mapa de calor simple para los datos proporcionados.
        
        Args:
            valores (dict): Diccionario con los valores a mostrar.
            titulo (str, optional): Título del mapa de calor.
            
        Returns:
            matplotlib.figure.Figure: La figura creada.
        """
        # Crear un DataFrame para un "mapa de calor"
        variables = list(valores.keys())
        valores_list = list(valores.values())
        
        # Crear una matriz para el mapa de calor
        df_calor = pd.DataFrame([valores_list], columns=variables)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df_calor, annot=True, cmap='coolwarm', ax=ax)
        plt.title(titulo)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        
        return fig
