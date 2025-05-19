import pyodbc
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
import joblib

# Conexión a la base de datos
def extraer_datos():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=CHANG;DATABASE=MierdiInvestigacion;UID=sa;PWD=Once;TrustServerCertificate=yes'
    )
    query = "SELECT LATITUDE, LONGITUDE, ELEVATION, WND_DIRECTION, WND_SPEED, CIG_HEIGHT, VIS_DISTANCE, TMP, DEW, SLP, LLOVIÓ FROM WeatherData"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Preprocesar datos
def preprocesar_datos(datos):
    X = datos.drop('LLOVIÓ', axis=1)
    y = datos['LLOVIÓ']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test, scaler

# Construir modelo de red neuronal
def construir_modelo(input_dim):
    modelo = Sequential([
        Dense(64, input_shape=(input_dim,), activation='relu'),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return modelo

# Guardar modelo entrenado
def guardar_modelo(modelo, scaler):
    modelo.save('modelo_lluvia.h5')
    joblib.dump(scaler, 'scaler.pkl')


# Predecir probabilidad de lluvia
def predecir_lluvia(modelo, scaler, nuevo_dato):
    nuevo_dato_scaled = scaler.transform([nuevo_dato])
    probabilidad = modelo.predict(nuevo_dato_scaled)
    print(f'Probabilidad de lluvia: {probabilidad[0][0] * 100:.2f}%')

# Ejecutar flujo principal
def main():
    print('Extrayendo datos de la base de datos...')
    datos = extraer_datos()
    print('Preprocesando datos...')
    X_train, X_test, y_train, y_test, scaler = preprocesar_datos(datos)

    print('Construyendo modelo de red neuronal...')
    modelo = construir_modelo(X_train.shape[1])

    print('Entrenando el modelo...')
    modelo.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

    print('Evaluando el modelo...')
    loss, accuracy = modelo.evaluate(X_test, y_test)
    print(f'Precisión del modelo: {accuracy * 100:.2f}%')

    print('Guardando el modelo...')
    guardar_modelo(modelo, scaler)

    # Predicción de ejemplo
    nuevo_dato = [25.685194, -109.080806, 4.87, 240, 3.1, 22000, 16093, 28.01, 13.01, 1008.51]
    predecir_lluvia(modelo, scaler, nuevo_dato)

if __name__ == "__main__":
    main()
