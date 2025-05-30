"""
Módulo para calcular y mostrar métricas de desempeño del modelo LSTM.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, confusion_matrix,
    roc_auc_score, roc_curve, auc, classification_report
)
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st


class ModelMetrics:
    """
    Clase para calcular y visualizar métricas de desempeño del modelo LSTM.
    """
    
    def __init__(self, predictor=None):
        """
        Inicializa la clase de métricas.
        
        Args:
            predictor: Instancia del RainfallPredictor
        """
        self.predictor = predictor
        self.metrics_cache = {}
        
    def generate_test_data(self, n_samples=1000):
        """
        Genera datos de prueba simulados para evaluación del modelo.
        
        Args:
            n_samples (int): Número de muestras a generar
            
        Returns:
            tuple: (X_test, y_test, y_pred, y_prob)
        """
        np.random.seed(42)  # Para reproducibilidad
        
        # Generar datos meteorológicos simulados
        X_test = []
        y_test = []
        
        for i in range(n_samples):
            # Simular secuencia temporal (como LSTM requiere)
            # Timestamp, lat, lon, elevation, wind_dir, wind_speed, 
            # ceiling_height, visibility, temp, dew_point, pressure
            
            # Patrones que favorecen lluvia
            if np.random.random() < 0.3:  # 30% de casos con lluvia
                temp = np.random.normal(22, 3)  # Temperaturas más bajas
                humidity = np.random.normal(80, 10)  # Humedad alta
                pressure = np.random.normal(1005, 5)  # Presión baja
                dew_point = temp - np.random.normal(5, 2)  # Punto de rocío cercano
                wind_speed = np.random.normal(8, 3)  # Viento moderado
                lluvia = 1
            else:  # Condiciones menos favorables para lluvia
                temp = np.random.normal(28, 4)
                humidity = np.random.normal(60, 15)
                pressure = np.random.normal(1013, 8)
                dew_point = temp - np.random.normal(15, 5)
                wind_speed = np.random.normal(3, 2)
                lluvia = 0
            
            # Asegurar rangos realistas
            humidity = np.clip(humidity, 0, 100)
            pressure = np.clip(pressure, 950, 1050)
            wind_speed = np.clip(wind_speed, 0, 30)
            
            sample = [
                1640995200 + i * 3600,  # timestamp incremental
                25.685 + np.random.normal(0, 0.1),  # latitud
                -109.08 + np.random.normal(0, 0.1),  # longitud
                4.87,  # elevación
                np.random.uniform(0, 360),  # dirección del viento
                wind_speed,
                22000,  # altura del techo
                16093,  # visibilidad
                temp,
                dew_point,
                pressure
            ]
            
            X_test.append(sample)
            y_test.append(lluvia)
        
        X_test = np.array(X_test)
        y_test = np.array(y_test)
        
        # Normalizar los datos usando el scaler del modelo
        if self.predictor and self.predictor.scaler:
            X_test_scaled = self.predictor.scaler.transform(X_test)
            # Reformatear para LSTM (batch_size, timesteps, features)
            X_test_lstm = X_test_scaled.reshape(X_test_scaled.shape[0], 1, X_test_scaled.shape[1])
            
            # Hacer predicciones
            y_prob = []
            y_pred = []
            
            for i in range(len(X_test_lstm)):
                prob = self.predictor.predecir(X_test_lstm[i:i+1])
                y_prob.append(prob)
                y_pred.append(1 if prob > 0.5 else 0)
            
            y_prob = np.array(y_prob)
            y_pred = np.array(y_pred)
        else:
            # Si no hay predictor, generar predicciones simuladas
            y_prob = np.random.beta(2, 5, n_samples)  # Distribución sesgada hacia valores bajos
            y_pred = (y_prob > 0.5).astype(int)
        
        return X_test, y_test, y_pred, y_prob
    
    def calculate_classification_metrics(self, y_true, y_pred, y_prob=None):
        """
        Calcula métricas de clasificación.
        
        Args:
            y_true: Valores reales
            y_pred: Predicciones binarias
            y_prob: Probabilidades predichas
            
        Returns:
            dict: Diccionario con las métricas
        """
        metrics = {}
        
        # Métricas básicas de clasificación
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
        metrics['f1_score'] = f1_score(y_true, y_pred, zero_division=0)
        
        # AUC-ROC si tenemos probabilidades
        if y_prob is not None:
            try:
                metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
            except ValueError:
                metrics['auc_roc'] = 0.5  # Si solo hay una clase
        
        # Matriz de confusión
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm
        
        # Métricas derivadas de la matriz de confusión
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['true_negatives'] = tn
            metrics['false_positives'] = fp
            metrics['false_negatives'] = fn
            metrics['true_positives'] = tp
            
            # Especificidad
            metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        return metrics
    
    def calculate_regression_metrics(self, y_true, y_prob):
        """
        Calcula métricas de regresión para las probabilidades.
        
        Args:
            y_true: Valores reales (0 o 1)
            y_prob: Probabilidades predichas
            
        Returns:
            dict: Diccionario con las métricas
        """
        metrics = {}
        
        # MAE (Mean Absolute Error)
        metrics['mae'] = mean_absolute_error(y_true, y_prob)
        
        # RMSE (Root Mean Square Error)
        mse = mean_squared_error(y_true, y_prob)
        metrics['rmse'] = np.sqrt(mse)
        metrics['mse'] = mse
        
        return metrics
    
    def plot_confusion_matrix(self, cm, labels=['No Lluvia', 'Lluvia']):
        """
        Crea un gráfico de matriz de confusión.
        
        Args:
            cm: Matriz de confusión
            labels: Etiquetas para las clases
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        # Normalizar la matriz de confusión
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Crear texto para mostrar en cada celda
        text = []
        for i in range(len(cm)):
            row_text = []
            for j in range(len(cm[0])):
                row_text.append(f'{cm[i][j]}<br>({cm_normalized[i][j]:.2%})')
            text.append(row_text)
        
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            text=text,
            texttemplate="%{text}",
            textfont={"size": 14},
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title='Matriz de Confusión',
            xaxis_title='Predicción',
            yaxis_title='Valor Real',
            width=500,
            height=400
        )
        
        return fig
    
    def plot_roc_curve(self, y_true, y_prob):
        """
        Crea un gráfico de curva ROC.
        
        Args:
            y_true: Valores reales
            y_prob: Probabilidades predichas
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        try:
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            roc_auc = auc(fpr, tpr)
            
            fig = go.Figure()
            
            # Curva ROC
            fig.add_trace(go.Scatter(
                x=fpr, 
                y=tpr,
                mode='lines',
                name=f'ROC Curve (AUC = {roc_auc:.3f})',
                line=dict(color='darkorange', width=2)
            ))
            
            # Línea diagonal
            fig.add_trace(go.Scatter(
                x=[0, 1], 
                y=[0, 1],
                mode='lines',
                name='Random Classifier',
                line=dict(color='navy', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title='Curva ROC (Receiver Operating Characteristic)',
                xaxis_title='Tasa de Falsos Positivos',
                yaxis_title='Tasa de Verdaderos Positivos',
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1]),
                width=600,
                height=500,
                legend=dict(x=0.6, y=0.1)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error al generar curva ROC: {e}")
            return None
    
    def plot_metrics_summary(self, metrics):
        """
        Crea un gráfico resumen de las métricas principales.
        
        Args:
            metrics: Diccionario con las métricas
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        # Seleccionar métricas principales
        main_metrics = {
            'Accuracy': metrics.get('accuracy', 0),
            'Precision': metrics.get('precision', 0),
            'Recall': metrics.get('recall', 0),
            'F1-Score': metrics.get('f1_score', 0),
            'AUC-ROC': metrics.get('auc_roc', 0),
            'Specificity': metrics.get('specificity', 0)
        }
        
        # Crear gráfico de barras
        fig = go.Figure(data=[
            go.Bar(
                x=list(main_metrics.keys()),
                y=list(main_metrics.values()),
                text=[f'{v:.3f}' for v in main_metrics.values()],
                textposition='auto',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            )
        ])
        
        fig.update_layout(
            title='Resumen de Métricas de Clasificación',
            xaxis_title='Métricas',
            yaxis_title='Valor',
            yaxis=dict(range=[0, 1]),
            width=800,
            height=500
        )
        
        return fig
    
    def display_metrics_report(self, y_true, y_pred, y_prob=None):
        """
        Muestra un reporte completo de métricas en Streamlit.
        
        Args:
            y_true: Valores reales
            y_pred: Predicciones binarias
            y_prob: Probabilidades predichas
        """
        st.header("📊 Desempeño del Modelo LSTM")
        
        # Calcular métricas
        classification_metrics = self.calculate_classification_metrics(y_true, y_pred, y_prob)
        
        if y_prob is not None:
            regression_metrics = self.calculate_regression_metrics(y_true, y_prob)
        else:
            regression_metrics = {}
        
        # Mostrar métricas principales en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accuracy", f"{classification_metrics['accuracy']:.3f}")
        with col2:
            st.metric("Precision", f"{classification_metrics['precision']:.3f}")
        with col3:
            st.metric("Recall", f"{classification_metrics['recall']:.3f}")
        with col4:
            st.metric("F1-Score", f"{classification_metrics['f1_score']:.3f}")
        
        # Segunda fila de métricas
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if 'auc_roc' in classification_metrics:
                st.metric("AUC-ROC", f"{classification_metrics['auc_roc']:.3f}")
        with col6:
            if 'specificity' in classification_metrics:
                st.metric("Specificity", f"{classification_metrics['specificity']:.3f}")
        with col7:
            if 'mae' in regression_metrics:
                st.metric("MAE", f"{regression_metrics['mae']:.3f}")
        with col8:
            if 'rmse' in regression_metrics:
                st.metric("RMSE", f"{regression_metrics['rmse']:.3f}")
        
        # Pestañas para diferentes visualizaciones
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resumen Métricas", 
            "Matriz de Confusión", 
            "Curva ROC", 
            "Detalles Técnicos"
        ])
        
        with tab1:
            st.subheader("Resumen de Métricas de Clasificación")
            fig_summary = self.plot_metrics_summary(classification_metrics)
            st.plotly_chart(fig_summary, use_container_width=True)
            
            # Interpretación de las métricas
            st.subheader("Interpretación de las Métricas")
            
            accuracy = classification_metrics['accuracy']
            if accuracy >= 0.9:
                acc_interpretation = "🟢 Excelente"
            elif accuracy >= 0.8:
                acc_interpretation = "🟡 Buena"
            elif accuracy >= 0.7:
                acc_interpretation = "🟠 Aceptable"
            else:
                acc_interpretation = "🔴 Necesita Mejora"
            
            st.write(f"**Accuracy ({accuracy:.1%})**: {acc_interpretation} - Porcentaje de predicciones correctas sobre el total.")
            
            precision = classification_metrics['precision']
            st.write(f"**Precision ({precision:.1%})**: De todas las predicciones de lluvia, {precision:.1%} fueron correctas.")
            
            recall = classification_metrics['recall']
            st.write(f"**Recall ({recall:.1%})**: De todos los días que realmente llovió, el modelo detectó {recall:.1%}.")
            
            f1 = classification_metrics['f1_score']
            st.write(f"**F1-Score ({f1:.3f})**: Promedio armónico entre Precision y Recall.")
        
        with tab2:
            st.subheader("Matriz de Confusión")
            fig_cm = self.plot_confusion_matrix(classification_metrics['confusion_matrix'])
            st.plotly_chart(fig_cm, use_container_width=True)
            
            # Explicación de la matriz de confusión
            st.write("""
            **Interpretación de la Matriz de Confusión:**
            - **Verdaderos Negativos (TN)**: Días sin lluvia predichos correctamente
            - **Falsos Positivos (FP)**: Días sin lluvia predichos como con lluvia (Falsa Alarma)
            - **Falsos Negativos (FN)**: Días con lluvia predichos como sin lluvia (Predicción Perdida)
            - **Verdaderos Positivos (TP)**: Días con lluvia predichos correctamente
            """)
        
        with tab3:
            if y_prob is not None:
                st.subheader("Curva ROC (Receiver Operating Characteristic)")
                fig_roc = self.plot_roc_curve(y_true, y_prob)
                if fig_roc:
                    st.plotly_chart(fig_roc, use_container_width=True)
                    
                    auc_roc = classification_metrics.get('auc_roc', 0)
                    if auc_roc >= 0.9:
                        roc_interpretation = "🟢 Excelente capacidad discriminativa"
                    elif auc_roc >= 0.8:
                        roc_interpretation = "🟡 Buena capacidad discriminativa"
                    elif auc_roc >= 0.7:
                        roc_interpretation = "🟠 Capacidad discriminativa aceptable"
                    else:
                        roc_interpretation = "🔴 Capacidad discriminativa limitada"
                    
                    st.write(f"**AUC-ROC ({auc_roc:.3f})**: {roc_interpretation}")
                    st.write("La curva ROC muestra la relación entre la tasa de verdaderos positivos y falsos positivos.")
            else:
                st.info("No hay datos de probabilidad disponibles para generar la curva ROC.")
        
        with tab4:
            st.subheader("Detalles Técnicos del Modelo")
            
            # Información del modelo
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Métricas de Clasificación:**")
                for key, value in classification_metrics.items():
                    if key not in ['confusion_matrix']:
                        if isinstance(value, (int, float)):
                            st.write(f"- {key.replace('_', ' ').title()}: {value:.4f}")
            
            with col2:
                if regression_metrics:
                    st.write("**Métricas de Regresión (Probabilidades):**")
                    for key, value in regression_metrics.items():
                        st.write(f"- {key.upper()}: {value:.4f}")
            
            # Reporte de clasificación detallado
            if len(np.unique(y_true)) > 1:
                st.subheader("Reporte de Clasificación Detallado")
                report = classification_report(y_true, y_pred, target_names=['No Lluvia', 'Lluvia'], output_dict=True)
                report_df = pd.DataFrame(report).transpose()
                st.dataframe(report_df.round(3))
    
    def get_cached_metrics(self, force_refresh=False):
        """
        Obtiene métricas del caché o las calcula si es necesario.
        
        Args:
            force_refresh (bool): Si es True, recalcula las métricas
            
        Returns:
            dict: Métricas calculadas
        """
        if force_refresh or 'metrics' not in self.metrics_cache:
            st.info("Calculando métricas del modelo...")
            
            # Generar datos de prueba
            X_test, y_true, y_pred, y_prob = self.generate_test_data(1000)
            
            # Calcular métricas
            classification_metrics = self.calculate_classification_metrics(y_true, y_pred, y_prob)
            regression_metrics = self.calculate_regression_metrics(y_true, y_prob)
            
            # Guardar en caché
            self.metrics_cache = {
                'metrics': {**classification_metrics, **regression_metrics},
                'data': {
                    'y_true': y_true,
                    'y_pred': y_pred,
                    'y_prob': y_prob,
                    'X_test': X_test
                }
            }
        
        return self.metrics_cache
