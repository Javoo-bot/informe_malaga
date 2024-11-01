import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class ProcesadorDatos:
    """Clase para procesar y limpiar datos meteorológicos."""
    
    @staticmethod
    def limpiar_valor_numerico(valor):
        """
        Convierte un valor a float manejando casos especiales.
        
        Args:
            valor: Valor a convertir que puede ser string o numérico
            
        Returns:
            float: Valor numérico limpio o None si no se puede convertir
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


class AnalizadorParqueTecnologico:
    """Clase para analizar ubicaciones candidatas para el parque tecnológico."""
    
    def __init__(self, archivo_csv):
        """
        Inicializa el analizador con la ruta del archivo CSV.
        
        Args:
            archivo_csv (str): Ruta al archivo CSV con los datos
        """
        self.archivo_csv = archivo_csv
        self.df_malaga = None
        self.estaciones_stats = None
        
    def cargar_y_procesar_datos(self):
        """Carga y procesa los datos iniciales."""
        # Leer y procesar datos
        df = pd.read_csv(self.archivo_csv)
        self.df_malaga = df[df['provincia'].str.contains('MALAGA', na=False)]
        
        # Convertir columnas numéricas
        columnas_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'altitud']
        for columna in columnas_numericas:
            self.df_malaga[columna] = self.df_malaga[columna].apply(
                ProcesadorDatos.limpiar_valor_numerico
            )
    
    def calcular_metricas(self):
        """Calcula métricas por estación."""
        self.estaciones_stats = self.df_malaga.groupby('nombre').agg({
            'tmed': ['mean', 'max'],
            'prec': 'sum',
            'altitud': 'first'
        }).round(2)
        
        # Aplanar los índices multinivel
        self.estaciones_stats.columns = [
            'temp_media', 'temp_maxima', 'precipitacion_total', 'altitud'
        ]
        self.estaciones_stats = self.estaciones_stats.reset_index()
    
    def calcular_scores(self):
        """Calcula las puntuaciones de riesgo para cada estación."""
        # Normalizar valores para escala 0-1
        for col, data in [
            ('temp_score', 'temp_media'),
            ('prec_score', 'precipitacion_total'),
            ('alt_score', 'altitud')
        ]:
            max_val = self.estaciones_stats[data].max()
            min_val = self.estaciones_stats[data].min()
            
            if col == 'prec_score' or col == 'alt_score':
                self.estaciones_stats[col] = 1 - (
                    (self.estaciones_stats[data] - min_val) / (max_val - min_val)
                )
            else:
                self.estaciones_stats[col] = (
                    (self.estaciones_stats[data] - min_val) / (max_val - min_val)
                )
        
        # Calcular puntuación final
        self.estaciones_stats['riesgo_total'] = (
            self.estaciones_stats['temp_score'] * 0.4 +
            self.estaciones_stats['prec_score'] * 0.3 +
            self.estaciones_stats['alt_score'] * 0.3
        ).round(3)
    
    def generar_heatmap(self):
        """Genera y guarda el mapa de calor de las puntuaciones."""
        plt.figure(figsize=(12, 8))
        scores = self.estaciones_stats[
            ['nombre', 'temp_score', 'prec_score', 'alt_score']
        ].set_index('nombre')
        
        sns.heatmap(scores, annot=True, cmap='YlOrRd', fmt='.2f')
        plt.title('Análisis de Riesgo por Estación')
        plt.tight_layout()
        
        # Asegurar que existe el directorio
        if not os.path.exists('graph'):
            os.makedirs('graph')
        
        plt.savefig(os.path.join('graph', 'analisis_riesgo_estaciones.png'))
        plt.close()
    
    def obtener_resultados(self):
        """
        Obtiene los resultados ordenados por riesgo.
        
        Returns:
            pandas.DataFrame: Resultados ordenados por puntuación de riesgo
        """
        return self.estaciones_stats.sort_values('riesgo_total', ascending=False)


def main():
    """Función principal que ejecuta el análisis completo."""
    try:
        # Inicializar analizador
        ruta_archivo = os.path.join('csv', 'datos_climatologicos_anuales.csv')
        analizador = AnalizadorParqueTecnologico(ruta_archivo)
        
        # Ejecutar análisis
        analizador.cargar_y_procesar_datos()
        analizador.calcular_metricas()
        analizador.calcular_scores()
        analizador.generar_heatmap()
        
        # Obtener y mostrar resultados
        resultados = analizador.obtener_resultados()
        print("\nRanking de estaciones por riesgo de problemas de temperatura:")
        print(resultados[[
            'nombre', 'temp_media', 'precipitacion_total', 
            'altitud', 'riesgo_total'
        ]].to_string())
        
        # Guardar resultados
        resultados.to_csv('analisis_parque_tecnologico.csv', index=False)
        
        print("\nAnálisis completado. Se han generado:")
        print("- analisis_parque_tecnologico.csv: Resultados detallados")
        print("- graph/analisis_riesgo_estaciones.png: Visualización del análisis de riesgo")
        
    except Exception as e:
        print(f"Error durante el análisis: {e}")


if __name__ == "__main__":
    main()