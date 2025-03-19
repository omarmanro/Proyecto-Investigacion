import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Ruta del archivo CSV
archivo = r"C:\Users\Carlo\Downloads\DatosLimpios.csv"  # Cambiar por la ruta real

# Cargar y procesar datos
df = pd.read_csv(archivo, sep=',', skipinitialspace=True, header=None)
df.columns = ['STATION', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'WND', 'CIG', 'VIS', 'TMP', 'DEW', 'SLP','RAIN']

df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
df['TMP'] = df['TMP'].astype(str).str.extract(r'([-+]?\d+)')[0].astype(float)
df = df.dropna(subset=['TMP'])
df['FECHA'] = df['DATE'].dt.date
df['HORA'] = df['DATE'].dt.hour

# Crear tabla pivote
pivot = df.pivot_table(index='FECHA', columns='HORA', values='TMP', aggfunc='mean')
pivot = pivot.interpolate(method='linear', axis=1)

# Verificar valores extremos
vmin, vmax = pivot.min().min(), pivot.max().max()

# 🔥 **Mejor visualización**
plt.figure(figsize=(16, 10))  # ⬆ Aumentar tamaño de la figura
sns.heatmap(pivot, cmap="coolwarm", linewidths=0.2, linecolor='gray', vmin=vmin, vmax=vmax)

# 🔄 **Rotar etiquetas del eje X**
plt.xticks(rotation=45, ha="right")  # Asegurar legibilidad

# 📌 **Etiquetas y título**
plt.title("📊 Mapa de calor de temperatura por día y hora", fontsize=14)
plt.xlabel("Hora del día", fontsize=12)
plt.ylabel("Fecha", fontsize=12)

# 🖥️ **Mostrar el gráfico correctamente**
plt.tight_layout()  # Ajusta automáticamente los márgenes

plt.show()
