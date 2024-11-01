import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class DatosMeteorologicos:
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


class ProcesadorMalaga:
    """Clase para procesar datos específicos de Málaga."""
    
    def __init__(self, archivo_csv):
        """
        Inicializa el procesador con la ruta del archivo CSV.
        
        Args:
            archivo_csv (str): Ruta al archivo CSV con los datos
        """
        self.archivo_csv = archivo_csv
        self.df_malaga = None
        
    def procesar_datos(self):
        """
        Procesa los datos del archivo CSV y aplica las transformaciones necesarias.
        
        Returns:
            pandas.DataFrame: DataFrame con los datos procesados de Málaga
        """
        # Leer el CSV
        df = pd.read_csv(self.archivo_csv)
        
        # Filtrar solo las estaciones de Málaga
        self.df_malaga = df[df['provincia'].str.contains('MALAGA', na=False)]
        
        # Convertir columnas numéricas
        columnas_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'velmedia', 
                            'racha', 'presMax', 'presMin']
        
        for columna in columnas_numericas:
            self.df_malaga[columna] = self.df_malaga[columna].apply(
                DatosMeteorologicos.limpiar_valor_numerico
            )
        
        # Convertir la fecha a datetime
        self.df_malaga['fecha'] = pd.to_datetime(self.df_malaga['fecha'])
        
        return self.df_malaga
    
    def generar_resumen(self):
        """
        Genera un resumen estadístico por estación.
        
        Returns:
            pandas.DataFrame: Resumen de estadísticas por estación
        """
        resumen_estaciones = self.df_malaga.groupby('nombre').agg({
            'tmed': ['mean', 'min', 'max'],
            'prec': 'sum',
            'racha': 'max'
        }).round(2)
        
        print("\nResumen de estaciones meteorológicas de Málaga:")
        print(resumen_estaciones)
        
        return resumen_estaciones
    
    def guardar_datos(self, nombre_archivo='datos_malaga.csv'):
        """
        Guarda los datos procesados en un archivo CSV.
        
        Args:
            nombre_archivo (str): Nombre del archivo de salida
        """
        self.df_malaga.to_csv(nombre_archivo, index=False)


class GeneradorGraficas:
    """Clase para generar visualizaciones de los datos meteorológicos."""
    
    def __init__(self, df_malaga):
        """
        Inicializa el generador con los datos a visualizar.
        
        Args:
            df_malaga (pandas.DataFrame): DataFrame con los datos de Málaga
        """
        self.df_malaga = df_malaga
    
    def generar_grafica_temperatura(self):
        """Genera y guarda la gráfica de temperatura media por estación."""
        plt.figure(figsize=(12, 6))
        
        for estacion in self.df_malaga['nombre'].unique():
            datos_estacion = self.df_malaga[self.df_malaga['nombre'] == estacion]
            datos_validos = datos_estacion.dropna(subset=['tmed'])
            if not datos_validos.empty:
                plt.plot(datos_validos['fecha'], datos_validos['tmed'], 
                        label=estacion)
        
        plt.title('Temperatura Media por Estación en Málaga')
        plt.xlabel('Fecha')
        plt.ylabel('Temperatura Media (°C)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('temperaturas_malaga.png')
        plt.close()
    
    def generar_grafica_precipitaciones(self):
        """Genera y guarda la gráfica de precipitaciones por estación."""
        plt.figure(figsize=(12, 6))
        
        for estacion in self.df_malaga['nombre'].unique():
            datos_estacion = self.df_malaga[self.df_malaga['nombre'] == estacion]
            datos_validos = datos_estacion.dropna(subset=['prec'])
            if not datos_validos.empty:
                plt.plot(datos_validos['fecha'], datos_validos['prec'], 
                        label=estacion)
        
        plt.title('Precipitaciones por Estación en Málaga')
        plt.xlabel('Fecha')
        plt.ylabel('Precipitación (mm)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('precipitaciones_malaga.png')
        plt.close()


def mostrar_estadisticas_basicas(df_malaga):
    """
    Muestra estadísticas básicas de las estaciones de Málaga.
    
    Args:
        df_malaga (pandas.DataFrame): DataFrame con los datos de Málaga
    """
    print("\nEstadísticas básicas:")
    print("\nNúmero de estaciones:", len(df_malaga['nombre'].unique()))
    
    print("\nEstaciones encontradas:")
    for estacion in df_malaga['nombre'].unique():
        print(f"- {estacion}")
    
    print("\nRango de fechas:")
    print(f"Desde: {df_malaga['fecha'].min()}")
    print(f"Hasta: {df_malaga['fecha'].max()}")


def main():
    """Función principal que ejecuta el procesamiento y análisis de datos."""
    archivo_csv = '../csv/datos_climatologicos_anuales.csv'
    
    try:
        # Inicializar y procesar datos
        procesador = ProcesadorMalaga(archivo_csv)
        df_malaga = procesador.procesar_datos()
        
        # Generar resumen y guardar datos
        procesador.generar_resumen()
        procesador.guardar_datos()
        
        # Mostrar estadísticas
        mostrar_estadisticas_basicas(df_malaga)
        
        # Generar gráficas
        generador = GeneradorGraficas(df_malaga)
        generador.generar_grafica_temperatura()
        generador.generar_grafica_precipitaciones()
        
        print("\nProcesamiento completado. Se han generado:")
        print("- datos_malaga.csv: Archivo con los datos filtrados")
        print("- temperaturas_malaga.png: Gráfica de temperaturas")
        print("- precipitaciones_malaga.png: Gráfica de precipitaciones")
        
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo {archivo_csv}")
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")


if __name__ == "__main__":
    main()