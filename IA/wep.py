import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ruta del archivo CSV
archivo = r"C:\Users\Carlo\Downloads\DatosLimpios.csv"  # Cambiar por la ruta real

# Cargar y procesar datos
df = pd.read_csv(archivo, sep=',', skipinitialspace=True, header=None)
df.columns = ['STATION', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'WND', 'CIG', 'VIS', 'TMP', 'DEW', 'SLP','RAIN']

df['HORA'] = pd.to_datetime(df['DATE']).dt.hour  

plt.figure(figsize=(10, 5))  
sns.histplot(df[df['RAIN'] == 1]['HORA'], bins=24, kde=True, color="blue")  
plt.title("Frecuencia de lluvia según la hora del día")  
plt.xlabel("Hora del día")  
plt.ylabel("Frecuencia de lluvia")  
plt.show()  
