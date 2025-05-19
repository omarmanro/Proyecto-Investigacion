"""
Script para generar un reporte del estado actual de la aplicación modular.
Este script verifica la presencia de todos los archivos necesarios 
y genera un informe en formato Markdown.
"""
import os
import datetime
import glob

def check_file(file_path):
    """
    Verifica si un archivo existe y obtiene su tamaño y última modificación.
    
    Args:
        file_path (str): Ruta al archivo.
        
    Returns:
        dict: Información del archivo o None si no existe.
    """
    if os.path.exists(file_path):
        size_kb = os.path.getsize(file_path) / 1024
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        return {
            'exists': True,
            'size_kb': size_kb,
            'last_modified': mod_time,
            'filename': os.path.basename(file_path)
        }
    else:
        return {
            'exists': False,
            'filename': os.path.basename(file_path)
        }

# Directorio base
base_dir = os.path.dirname(os.path.abspath(__file__))

# Lista de archivos esenciales
essential_files = [
    "app.py",
    "streamlit_app.py",
    "weather_api_client.py",
    "weather_data_processor.py",
    "rainfall_predictor.py",
    "weather_visualizer.py",
    "modelo_lluvia_lstm.h5",
    "scaler_lstm.pkl",
    "requirements.txt",
    "README.md"
]

# Verificar archivos
file_reports = {}
for file in essential_files:
    file_path = os.path.join(base_dir, file)
    file_reports[file] = check_file(file_path)

# Contar archivos Python adicionales (no esenciales)
all_python_files = glob.glob(os.path.join(base_dir, "*.py"))
additional_py_files = [f for f in all_python_files if os.path.basename(f) not in essential_files]
additional_file_reports = {}
for file in additional_py_files:
    additional_file_reports[os.path.basename(file)] = check_file(file)

# Generar informe
report = f"""# Informe de Estado - Aplicación Modular de Predicción de Lluvia

## Generado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Archivos Esenciales

| Archivo | Estado | Tamaño (KB) | Última Modificación |
|---------|--------|-------------|---------------------|
"""

for file, info in file_reports.items():
    if info['exists']:
        report += f"| {file} | ✅ Presente | {info['size_kb']:.1f} KB | {info['last_modified'].strftime('%Y-%m-%d %H:%M:%S')} |\n"
    else:
        report += f"| {file} | ❌ No encontrado | - | - |\n"

report += """
## Archivos Adicionales

| Archivo | Tamaño (KB) | Última Modificación | Propósito |
|---------|-------------|---------------------|-----------|
"""

purpose_map = {
    "verify_structure.py": "Script para verificar la estructura de la aplicación",
    "verify_imports.py": "Script para verificar las importaciones de módulos",
    "verify_with_log.py": "Script para verificar componentes con registro de log",
    "test_components.py": "Pruebas unitarias para los componentes"
}

for file, info in additional_file_reports.items():
    purpose = purpose_map.get(file, "Archivo auxiliar")
    report += f"| {file} | {info['size_kb']:.1f} KB | {info['last_modified'].strftime('%Y-%m-%d %H:%M:%S')} | {purpose} |\n"

report += """
## Estructura de Archivos

```
py_modular/
│
├── app.py                  # Punto de entrada principal
├── streamlit_app.py        # Implementación de la aplicación Streamlit
├── weather_api_client.py   # Cliente API para datos meteorológicos
├── weather_data_processor.py # Procesamiento de datos meteorológicos
├── rainfall_predictor.py   # Predictor de lluvia (modelo LSTM)
├── weather_visualizer.py   # Visualizaciones de datos meteorológicos
├── modelo_lluvia_lstm.h5   # Modelo LSTM pre-entrenado
├── scaler_lstm.pkl         # Scaler para normalización de datos
├── requirements.txt        # Dependencias de la aplicación
├── README.md               # Documentación general del proyecto
├── MANUAL_USUARIO.md       # Manual de usuario detallado
"""

for file in additional_file_reports:
    report += f"├── {file}{' '*max(1, 25-len(file))}# {purpose_map.get(file, 'Archivo auxiliar')}\n"

report += "```\n\n"

report += """
## Estado General

"""

missing_files = [file for file, info in file_reports.items() if not info['exists']]
if missing_files:
    report += f"⚠️ **Atención**: Faltan {len(missing_files)} archivos esenciales: {', '.join(missing_files)}\n\n"
    report += "Se recomienda asegurarse de que todos los archivos esenciales estén presentes antes de ejecutar la aplicación.\n\n"
else:
    report += "✅ **Todos los archivos esenciales están presentes**. La aplicación está lista para ser ejecutada.\n\n"
    report += "Para iniciar la aplicación, utilice el siguiente comando:\n\n"
    report += "```bash\nstreamlit run app.py\n```\n\n"

report += "## Pasos Siguientes Recomendados\n\n"
report += "1. Revisar la documentación en `README.md` y `MANUAL_USUARIO.md`\n"
report += "2. Ejecutar la aplicación y verificar su funcionamiento\n"
report += "3. Explorar el código fuente para entender la estructura modular\n"
report += "4. Considerar posibles mejoras o extensiones de la funcionalidad\n"

# Guardar informe
report_path = os.path.join(base_dir, "INFORME_ESTADO.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)

print(f"Informe generado en: {report_path}")

# También imprimir un resumen en consola
print("\nResumen de estado:")
missing = [file for file, info in file_reports.items() if not info['exists']]
if missing:
    print(f"⚠️ Faltan {len(missing)} archivos esenciales: {', '.join(missing)}")
else:
    print("✅ Todos los archivos esenciales están presentes")
print(f"📁 {len(additional_file_reports)} archivos adicionales encontrados")
print(f"📊 Informe detallado generado en INFORME_ESTADO.md")
