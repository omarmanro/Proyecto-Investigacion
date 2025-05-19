import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve, auc
import plotly.graph_objects as go

class WeatherVisualizer:
    def __init__(self, df, model, scaler):
        """
        Inicializa la clase con el DataFrame, el modelo entrenado y el scaler.
        """
        self.df = df
        self.model = model
        self.scaler = scaler

    def plot_roc_curve(self):
        """
        Genera y muestra la curva ROC junto con el valor AUC.
        """
        # Preparar los datos
        X = self.df.drop(columns=['LLOVIÓ'])
        y = self.df['LLOVIÓ']
        X_scaled = self.scaler.transform(X)

        # Obtener las probabilidades predichas
        y_scores = self.model.predict(X_scaled).ravel()

        # Calcular la curva ROC y el AUC
        fpr, tpr, thresholds = roc_curve(y, y_scores)
        roc_auc = auc(fpr, tpr)

        # Graficar la curva ROC
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlabel('Tasa de Falsos Positivos')
        plt.ylabel('Tasa de Verdaderos Positivos')
        plt.title('Curva ROC')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.show()

    def plot_spider_chart(self, variables, group_column):
        """
        Genera un gráfico de radar (spider chart) para comparar múltiples variables meteorológicas.
        
        :param variables: Lista de nombres de columnas a incluir en el gráfico.
        :param group_column: Columna para agrupar los datos (por ejemplo, tipo de tormenta).
        """
        # Calcular la media de las variables por grupo
        df_grouped = self.df.groupby(group_column)[variables].mean().reset_index()

        # Preparar los datos para el gráfico
        categories = variables
        fig = go.Figure()

        for i in range(len(df_grouped)):
            fig.add_trace(go.Scatterpolar(
                r=df_grouped.loc[i, variables].values,
                theta=categories,
                fill='toself',
                name=str(df_grouped.loc[i, group_column])
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            showlegend=True,
            title='Gráfico de Radar de Variables Meteorológicas'
        )

        fig.show()

    def plot_scatter(self, x_var, y_var, hue=None):
        """
        Genera un diagrama de dispersión entre dos variables.
        
        :param x_var: Nombre de la variable para el eje X.
        :param y_var: Nombre de la variable para el eje Y.
        :param hue: (Opcional) Variable categórica para colorear los puntos.
        """
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=self.df, x=x_var, y=y_var, hue=hue)
        plt.title(f'Diagrama de Dispersión: {x_var} vs {y_var}')
        plt.xlabel(x_var)
        plt.ylabel(y_var)
        plt.grid(True)
        plt.show()

    def plot_heatmap(self, value_column, lat_column='LATITUDE', lon_column='LONGITUDE'):
        """
        Genera un mapa de calor geoespacial basado en una variable específica.
        
        :param value_column: Nombre de la columna con los valores a visualizar.
        :param lat_column: Nombre de la columna de latitud.
        :param lon_column: Nombre de la columna de longitud.
        """
        # Crear una tabla dinámica para el mapa de calor
        heatmap_data = self.df.pivot_table(index=lat_column, columns=lon_column, values=value_column, aggfunc='mean')

        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, cmap='coolwarm', cbar_kws={'label': value_column})
        plt.title(f'Mapa de Calor Geoespacial de {value_column}')
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.show()
