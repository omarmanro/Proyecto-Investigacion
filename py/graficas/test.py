import unittest
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from graficas import WeatherVisualizer

class TestWeatherVisualizer(unittest.TestCase):
    def setUp(self):
        """
        Configura los datos y el modelo para las pruebas.
        """
        # Crear un DataFrame de ejemplo
        data = {
            'LATITUDE': [25.685, 25.686, 25.687],
            'LONGITUDE': [-109.080, -109.081, -109.082],
            'ELEVATION': [4.87, 4.88, 4.89],
            'TMP': [28.0, 29.0, 30.0],
            'DEW': [13.0, 14.0, 15.0],
            'SLP': [1008.5, 1009.5, 1010.5],
            'LLOVIÓ': [1, 0, 1]
        }
        self.df = pd.DataFrame(data)

        # Crear un modelo y un scaler de ejemplo
        self.scaler = StandardScaler()
        X = self.df.drop(columns=['LLOVIÓ'])
        self.scaler.fit(X)
        self.model = RandomForestClassifier()
        self.model.fit(self.scaler.transform(X), self.df['LLOVIÓ'])

        # Inicializar el visualizador
        self.visualizer = WeatherVisualizer(self.df, self.model, self.scaler)

    def test_plot_roc_curve(self):
        """
        Prueba que la curva ROC se genere sin errores.
        """
        try:
            self.visualizer.plot_roc_curve()
        except Exception as e:
            self.fail(f"plot_roc_curve() lanzó una excepción: {e}")

    def test_plot_spider_chart(self):
        """
        Prueba que el gráfico de radar se genere sin errores.
        """
        try:
            self.visualizer.plot_spider_chart(variables=['TMP', 'DEW', 'SLP'], group_column='LLOVIÓ')
        except Exception as e:
            self.fail(f"plot_spider_chart() lanzó una excepción: {e}")

    def test_plot_scatter(self):
        """
        Prueba que el diagrama de dispersión se genere sin errores.
        """
        try:
            self.visualizer.plot_scatter(x_var='TMP', y_var='DEW', hue='LLOVIÓ')
        except Exception as e:
            self.fail(f"plot_scatter() lanzó una excepción: {e}")

    def test_plot_heatmap(self):
        """
        Prueba que el mapa de calor se genere sin errores.
        """
        try:
            self.visualizer.plot_heatmap(value_column='TMP', lat_column='LATITUDE', lon_column='LONGITUDE')
        except Exception as e:
            self.fail(f"plot_heatmap() lanzó una excepción: {e}")

if __name__ == "__main__":
    unittest.main()
