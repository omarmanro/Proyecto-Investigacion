import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import joblib

# 1. Extraer los datos desde la base de datos
def extraer_datos():
    engine = create_engine('mssql+pyodbc://sa:Once@CHANG/MierdiInvestigacion?driver=SQL+Server&TrustServerCertificate=yes')
    query = "SELECT DATE, LATITUDE, LONGITUDE, ELEVATION, WND_DIRECTION, WND_SPEED, CIG_HEIGHT, VIS_DISTANCE, TMP, DEW, SLP, LLOVIÓ FROM WeatherData"
    df = pd.read_sql(query, engine)
    return df

df = extraer_datos()
print(df.columns)

# 2. Preprocesamiento
df = df.sort_values(by='DATE')  # Ordenar por fecha
df['DATE'] = df['DATE'].astype(np.int64) // 10**9  # Convertir fecha a timestamp

# 3. Normalización
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df.drop(columns=['LLOVIÓ']))  # Escalar excepto la variable objetivo

# 4. Crear secuencias de datos para LSTM
def create_sequences(data, target, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(target[i+seq_length])
    return np.array(X), np.array(y)

seq_length = 10  # Tomar los últimos 10 registros para predecir el siguiente
X, y = create_sequences(df_scaled, df['LLOVIÓ'].values, seq_length)

# 5. División en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 6. Construcción del modelo LSTM
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(seq_length, X.shape[2])),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25, activation='relu'),
    Dense(1, activation='sigmoid')  # Salida binaria (0 o 1, lluvia/no lluvia)
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 7. Entrenar el modelo
model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test))

# 8. Guardar el modelo entrenado y el scaler
model.save('modelo_lluvia_lstm.h5')
joblib.dump(scaler, 'scaler_lstm.pkl')
