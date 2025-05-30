"""
Test de conexión para el LLM (LM Studio).
Este script comprueba que el LLM está disponible y funcionando correctamente.
"""
import sys
import os
import time
from datetime import datetime
import json

# Agregar el directorio src al path para poder importar los módulos
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    # Importación directa sin referencias relativas
    from llm_client_new import LLMClient
    from config import config as config_obj
    print("✓ Importaciones exitosas")
except ImportError as e:
    print(f"✗ Error al importar módulos: {e}")
    print(f"Ruta src: {src_path}")
    print(f"Archivos en src: {os.listdir(src_path) if os.path.exists(src_path) else 'Directorio no encontrado'}")
    sys.exit(1)

def test_configuracion_llm():
    """Verifica que la configuración del LLM esté correcta."""
    print("\n" + "="*60)
    print("VERIFICANDO CONFIGURACIÓN DEL LLM")
    print("="*60)
    print(f"URL de la API: {config_obj.LLM_API_URL}")
    print(f"Modelo: {config_obj.LLM_MODEL_NAME}")
    print(f"Max tokens: {config_obj.LLM_MAX_TOKENS}")
    print(f"Temperature: {config_obj.LLM_TEMPERATURE}")

    if config_obj.LLM_API_URL and config_obj.LLM_MODEL_NAME:
        print("✓ Configuración básica presente")
        return True
    else:
        print("✗ Configuración incompleta")
        return False

def test_conexion_basica():
    """Prueba la conexión básica al LLM."""
    print("\n" + "="*60)
    print("PROBANDO CONEXIÓN BÁSICA AL LLM")
    print("="*60)
    
    try:
        # Crear cliente LLM
        client = LLMClient()
        print("✓ Cliente LLM creado exitosamente")
        
        # Probar conexión
        print("Probando conexión al servidor LM Studio...")
        conexion_exitosa = client.test_conexion()
        
        if conexion_exitosa:
            print("✓ Conexión exitosa al LM Studio")
            return True, client
        else:
            print("✗ No se pudo conectar al LM Studio")
            print("  Asegúrate de que LM Studio esté ejecutándose en http://localhost:1234")
            return False, None
            
    except Exception as e:
        print(f"✗ Error al crear cliente o probar conexión: {e}")
        return False, None

def test_funcionalidad_llm(client):
    """Prueba la funcionalidad básica del LLM."""
    print("\n" + "="*60)
    print("PROBANDO FUNCIONALIDAD DEL LLM")
    print("="*60)
    
    # Test 1: Consulta simple
    print("\n1. Probando consulta simple...")
    try:
        respuesta = client._hacer_peticion("Hola, ¿puedes ayudarme con un análisis meteorológico?")
        if respuesta:
            print("✓ Consulta simple exitosa")
            print(f"  Respuesta (primeros 100 caracteres): {respuesta[:100]}...")
        else:
            print("✗ No se recibió respuesta a la consulta simple")
            return False
    except Exception as e:
        print(f"✗ Error en consulta simple: {e}")
        return False
    
    # Test 2: Análisis meteorológico básico
    print("\n2. Probando análisis meteorológico...")
    datos_test = {
        'temperature': 25.5,
        'humidity': 78,
        'dew_point': 18.2,
        'pressure': 1013.2,
        'wind_speed': 5.5
    }
    probabilidad_lluvia = 0.65
    
    try:
        analisis = client.generar_analisis_prediccion(datos_test, probabilidad_lluvia)
        if analisis:
            print("✓ Análisis meteorológico generado exitosamente")
            print(f"  Análisis (primeros 150 caracteres): {analisis[:150]}...")
        else:
            print("✗ No se pudo generar análisis meteorológico")
            return False
    except Exception as e:
        print(f"✗ Error en análisis meteorológico: {e}")
        return False
    
    # Test 3: Explicación de gráficas
    print("\n3. Probando explicación de gráficas...")
    try:
        explicacion = client.explicar_graficas('radar', datos_test, probabilidad_lluvia)
        if explicacion:
            print("✓ Explicación de gráficas generada exitosamente")
            print(f"  Explicación (primeros 100 caracteres): {explicacion[:100]}...")
        else:
            print("✗ No se pudo generar explicación de gráficas")
            return False
    except Exception as e:
        print(f"✗ Error en explicación de gráficas: {e}")
        return False
    
    # Test 4: Reporte meteorológico
    print("\n4. Probando reporte meteorológico...")
    try:
        # Crear objeto de ubicación requerido por generar_reporte_completo
        ubicacion = {
            'lat': 24.8019,
            'lon': -107.3940  # Coordenadas de Culiacán
        }
        reporte = client.generar_reporte_completo(datos_test, probabilidad_lluvia, ubicacion)
        if reporte:
            print("✓ Reporte meteorológico generado exitosamente")
            print(f"  Reporte (primeros 150 caracteres): {reporte[:150]}...")
        else:
            print("✗ No se pudo generar reporte meteorológico")
            return False
    except Exception as e:
        print(f"✗ Error en reporte meteorológico: {e}")
        return False
    
    return True

def test_performance_llm(client):
    """Prueba el rendimiento del LLM."""
    print("\n" + "="*60)
    print("PROBANDO RENDIMIENTO DEL LLM")
    print("="*60)
    
    # Medir tiempo de respuesta
    consultas_test = [
        "¿Qué factores indican alta probabilidad de lluvia?",
        "Explica brevemente cómo interpretar la humedad relativa.",
        "¿Cuál es la diferencia entre temperatura y punto de rocío?"
    ]
    
    tiempos = []
    
    for i, consulta in enumerate(consultas_test, 1):
        print(f"\nConsulta {i}: {consulta[:50]}...")
        
        inicio = time.time()
        try:
            respuesta = client._hacer_peticion(consulta)
            fin = time.time()
            
            if respuesta:
                tiempo_respuesta = fin - inicio
                tiempos.append(tiempo_respuesta)
                print(f"✓ Respuesta en {tiempo_respuesta:.2f} segundos")
            else:
                print("✗ Sin respuesta")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if tiempos:
        tiempo_promedio = sum(tiempos) / len(tiempos)
        print(f"\n📊 Estadísticas de rendimiento:")
        print(f"  Tiempo promedio de respuesta: {tiempo_promedio:.2f} segundos")
        print(f"  Tiempo mínimo: {min(tiempos):.2f} segundos")
        print(f"  Tiempo máximo: {max(tiempos):.2f} segundos")
        
        if tiempo_promedio < 10:
            print("✓ Rendimiento bueno (< 10s)")
        elif tiempo_promedio < 30:
            print("⚠ Rendimiento aceptable (10-30s)")
        else:
            print("⚠ Rendimiento lento (> 30s)")
    
    return len(tiempos) == len(consultas_test)

def guardar_log_test(resultados):
    """Guarda los resultados del test en un archivo log."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"test_llm_log_{timestamp}.txt"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Test de conexión LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for test, resultado in resultados.items():
                f.write(f"{test}: {'✓ EXITOSO' if resultado else '✗ FALLIDO'}\n")
            
            f.write(f"\nConfiguracion utilizada:\n")
            f.write(f"  URL API: {config_obj.LLM_API_URL}\n")
            f.write(f"  Modelo: {config_obj.LLM_MODEL_NAME}\n")
            f.write(f"  Max tokens: {config_obj.LLM_MAX_TOKENS}\n")
            f.write(f"  Temperature: {config_obj.LLM_TEMPERATURE}\n")
        
        print(f"\n📄 Log guardado en: {log_file}")
        
    except Exception as e:
        print(f"⚠ No se pudo guardar el log: {e}")

def main():
    """Función principal que ejecuta todos los tests."""
    print("🧪 INICIANDO TEST DE CONEXIÓN LLM")
    print("="*60)
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # Test 1: Configuración
    resultados['Configuración'] = test_configuracion_llm()
    
    # Test 2: Conexión básica
    conexion_exitosa, client = test_conexion_basica()
    resultados['Conexión básica'] = conexion_exitosa
    
    if conexion_exitosa and client:
        # Test 3: Funcionalidad
        resultados['Funcionalidad'] = test_funcionalidad_llm(client)
        
        # Test 4: Rendimiento
        resultados['Rendimiento'] = test_performance_llm(client)
    else:
        print("\n⚠ Saltando tests de funcionalidad y rendimiento debido a fallo de conexión")
        resultados['Funcionalidad'] = False
        resultados['Rendimiento'] = False
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL DEL TEST")
    print("="*60)
    
    tests_exitosos = sum(1 for resultado in resultados.values() if resultado)
    total_tests = len(resultados)
    
    for test, resultado in resultados.items():
        status = "✓ EXITOSO" if resultado else "✗ FALLIDO"
        print(f"{test}: {status}")
    
    print(f"\nResultado general: {tests_exitosos}/{total_tests} tests exitosos")
    
    if tests_exitosos == total_tests:
        print("🎉 ¡Todos los tests pasaron! El LLM está funcionando correctamente.")
    elif tests_exitosos > 0:
        print("⚠ Algunos tests fallaron. Revisar configuración o estado del LM Studio.")
    else:
        print("❌ Todos los tests fallaron. El LLM no está disponible.")
    
    # Guardar log
    guardar_log_test(resultados)
    
    # Mostrar sugerencias si hay fallos
    if tests_exitosos < total_tests:
        print("\n💡 SUGERENCIAS:")
        if not resultados['Conexión básica']:
            print("  1. Verificar que LM Studio esté ejecutándose")
            print("  2. Confirmar que el servidor esté en http://localhost:1234")
            print("  3. Verificar que un modelo esté cargado en LM Studio")
        
        if not resultados['Funcionalidad']:
            print("  4. Verificar que el modelo esté respondiendo correctamente")
            print("  5. Revisar logs de LM Studio por errores")
        
        if not resultados['Rendimiento']:
            print("  6. Considerar usar un modelo más pequeño para mejor rendimiento")
            print("  7. Verificar recursos del sistema (RAM, CPU)")

if __name__ == "__main__":
    main()
