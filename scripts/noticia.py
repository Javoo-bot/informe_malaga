import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def analizar_candidatos_parque_tecnologico(archivo_csv):
    """
    Analiza las estaciones meteorológicas para identificar posibles ubicaciones
    del parque tecnológico basado en criterios específicos.
    """
    # Leer y procesar datos
    df = pd.read_csv(archivo_csv)
    df_malaga = df[df['provincia'].str.contains('MALAGA', na=False)]
    
    # Convertir columnas numéricas
    columnas_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'altitud']
    
    # Aplicar la función de limpieza a todas las columnas numéricas
    for columna in columnas_numericas:
        df_malaga[columna] = df_malaga[columna].apply(limpiar_valor_numerico)
    
    # Análisis por estación
    analisis_estaciones = pd.DataFrame()
    
    # Calcular métricas por estación
    estaciones_stats = df_malaga.groupby('nombre').agg({
        'tmed': ['mean', 'max'],
        'prec': 'sum',
        'altitud': 'first'
    }).round(2)
    
    # Aplanar los índices multinivel
    estaciones_stats.columns = ['temp_media', 'temp_maxima', 'precipitacion_total', 'altitud']
    estaciones_stats = estaciones_stats.reset_index()
    
    # Calcular puntuación de riesgo
    # Normalizar valores para que estén en escala 0-1
    estaciones_stats['temp_score'] = (estaciones_stats['temp_media'] - estaciones_stats['temp_media'].min()) / (estaciones_stats['temp_media'].max() - estaciones_stats['temp_media'].min())
    estaciones_stats['prec_score'] = 1 - (estaciones_stats['precipitacion_total'] - estaciones_stats['precipitacion_total'].min()) / (estaciones_stats['precipitacion_total'].max() - estaciones_stats['precipitacion_total'].min())
    estaciones_stats['alt_score'] = 1 - (estaciones_stats['altitud'] - estaciones_stats['altitud'].min()) / (estaciones_stats['altitud'].max() - estaciones_stats['altitud'].min())
    
    # Puntuación final (mayor puntuación = mayor probabilidad de ser el parque tecnológico)
    estaciones_stats['riesgo_total'] = (estaciones_stats['temp_score'] * 0.4 + 
                                      estaciones_stats['prec_score'] * 0.3 + 
                                      estaciones_stats['alt_score'] * 0.3).round(3)
    
    # Ordenar por puntuación de riesgo
    estaciones_riesgo = estaciones_stats.sort_values('riesgo_total', ascending=False)
    
    # Generar gráfico de calor con las puntuaciones
    plt.figure(figsize=(12, 8))
    scores = estaciones_riesgo[['nombre', 'temp_score', 'prec_score', 'alt_score']].set_index('nombre')
    sns.heatmap(scores, annot=True, cmap='YlOrRd', fmt='.2f')
    plt.title('Análisis de Riesgo por Estación')
    plt.tight_layout()
    
    # Asegurar que el directorio 'graph' existe
    if not os.path.exists('graph'):
        os.makedirs('graph')
        
    plt.savefig(os.path.join('graph', 'analisis_riesgo_estaciones.png'))
    plt.close()
    
    return estaciones_riesgo

if __name__ == "__main__":
    try:
        # Realizar análisis
        ruta_archivo = os.path.join('csv', 'datos_climatologicos_anuales.csv')
        resultados = analizar_candidatos_parque_tecnologico(ruta_archivo)
                
        print("\nRanking de estaciones por riesgo de problemas de temperatura:")
        print(resultados[['nombre', 'temp_media', 'precipitacion_total', 'altitud', 'riesgo_total']].to_string())
        
        # Guardar resultados en CSV
        resultados.to_csv('analisis_parque_tecnologico.csv', index=False)
        
        print("\nAnálisis completado. Se han generado:")
        print("- analisis_parque_tecnologico.csv: Resultados detallados")
        print("- graph/analisis_riesgo_estaciones.png: Visualización del análisis de riesgo")
        
    except Exception as e:
        print(f"Error durante el análisis: {e}")