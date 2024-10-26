import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def limpiar_valor_numerico(valor):
    """
    Convierte un valor a float manejando casos especiales:
    - Reemplaza comas por puntos
    - Maneja valores especiales como 'Ip' y 'Varias'
    """
    if pd.isna(valor) or valor == '' or valor == 'Varias':
        return None
    elif valor == 'Ip':  # Ip significa "inapreciable" en precipitación
        return 0.0
    else:
        try:
            return float(str(valor).replace(',', '.'))
        except ValueError:
            return None

def procesar_datos_malaga(archivo_csv):
    # Leer el CSV
    df = pd.read_csv(archivo_csv)
    
    # Filtrar solo las estaciones de Málaga
    df_malaga = df[df['provincia'].str.contains('MALAGA', na=False)]
    
    # Convertir columnas numéricas
    columnas_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'velmedia', 'racha', 'presMax', 'presMin']
    
    for columna in columnas_numericas:
        df_malaga[columna] = df_malaga[columna].apply(limpiar_valor_numerico)
    
    # Convertir la fecha a datetime
    df_malaga['fecha'] = pd.to_datetime(df_malaga['fecha'])
    
    # Guardar los datos de Málaga en un nuevo CSV
    df_malaga.to_csv('datos_malaga.csv', index=False)
    
    # Crear un resumen por estación
    resumen_estaciones = df_malaga.groupby('nombre').agg({
        'tmed': ['mean', 'min', 'max'],
        'prec': 'sum',
        'racha': 'max'
    }).round(2)
    
    print("\nResumen de estaciones meteorológicas de Málaga:")
    print(resumen_estaciones)
    
    return df_malaga

def generar_graficas(df_malaga):
    if df_malaga.empty:
        print("No hay datos para generar gráficas")
        return
        
    # Gráfica de temperatura media por estación
    plt.figure(figsize=(12, 6))
    for estacion in df_malaga['nombre'].unique():
        datos_estacion = df_malaga[df_malaga['nombre'] == estacion]
        datos_validos = datos_estacion.dropna(subset=['tmed'])
        if not datos_validos.empty:
            plt.plot(datos_validos['fecha'], datos_validos['tmed'], label=estacion)
    
    plt.title('Temperatura Media por Estación en Málaga')
    plt.xlabel('Fecha')
    plt.ylabel('Temperatura Media (°C)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('temperaturas_malaga.png')
    plt.close()
    
    # Gráfica de precipitaciones
    plt.figure(figsize=(12, 6))
    for estacion in df_malaga['nombre'].unique():
        datos_estacion = df_malaga[df_malaga['nombre'] == estacion]
        datos_validos = datos_estacion.dropna(subset=['prec'])
        if not datos_validos.empty:
            plt.plot(datos_validos['fecha'], datos_validos['prec'], label=estacion)
    
    plt.title('Precipitaciones por Estación en Málaga')
    plt.xlabel('Fecha')
    plt.ylabel('Precipitación (mm)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('precipitaciones_malaga.png')
    plt.close()

def mostrar_estadisticas_basicas(df_malaga):
    """
    Muestra estadísticas básicas de las estaciones de Málaga
    """
    print("\nEstadísticas básicas:")
    print("\nNúmero de estaciones:", len(df_malaga['nombre'].unique()))
    print("\nEstaciones encontradas:")
    for estacion in df_malaga['nombre'].unique():
        print(f"- {estacion}")
    
    print("\nRango de fechas:")
    print(f"Desde: {df_malaga['fecha'].min()}")
    print(f"Hasta: {df_malaga['fecha'].max()}")

if __name__ == "__main__":
    # Nombre del archivo CSV generado por el script anterior
    archivo_csv = 'datos_climatologicos_anuales.csv'
    
    try:
        # Procesar los datos
        df_malaga = procesar_datos_malaga(archivo_csv)
        
        # Mostrar estadísticas básicas
        mostrar_estadisticas_basicas(df_malaga)
        
        # Generar gráficas
        generar_graficas(df_malaga)
        
        print("\nProcesamiento completado. Se han generado:")
        print("- datos_malaga.csv: Archivo con los datos filtrados")
        print("- temperaturas_malaga.png: Gráfica de temperaturas")
        print("- precipitaciones_malaga.png: Gráfica de precipitaciones")
        
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo {archivo_csv}")
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")