import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv


def cargar_api_key():
    """
    Carga y verifica la API key desde las variables de entorno.
    
    Returns:
        str: API key de AEMET
    
    Raises:
        SystemExit: Si no se encuentra la API key
    """
    load_dotenv()
    api_key = os.getenv('API_KEY')
    
    if not api_key:
        print("Error: La API_KEY no se encuentra definida. Asegúrate de que esté en el archivo .env")
        exit()
    
    return api_key


def obtener_datos(fecha_inicio, fecha_final, api_key):
    """
    Obtiene datos climatológicos para un rango de fechas específico.
    
    Args:
        fecha_inicio (str): Fecha inicial en formato ISO
        fecha_final (str): Fecha final en formato ISO
        api_key (str): API key de AEMET
    
    Returns:
        list: Datos climatológicos si la petición es exitosa, None en caso contrario
    """
    URL_BASE = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos"
    url = f"{URL_BASE}/fechaini/{fecha_inicio}/fechafin/{fecha_final}/todasestaciones?api_key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            datos_json = response.json()
            datos_url = datos_json.get('datos')
            if datos_url:
                response_data = requests.get(datos_url)
                if response_data.status_code == 200:
                    return response_data.json()
                else:
                    print(f"Error al obtener los datos de {fecha_inicio} a {fecha_final}: {response_data.status_code}")
        else:
            print(f"Error al acceder a la API: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión a la API: {e}")
    
    return None


def obtener_rango_fechas(año):
    """
    Calcula el rango de fechas para el año especificado.
    
    Args:
        año (int): Año para el cual se quieren obtener los datos
    
    Returns:
        tuple: Fecha inicial y final como objetos datetime
    """
    return datetime(año, 1, 1), datetime(año, 12, 31)


def formatear_fecha(fecha):
    """
    Formatea una fecha al formato requerido por la API.
    
    Args:
        fecha (datetime): Fecha a formatear
    
    Returns:
        str: Fecha formateada en formato ISO
    """
    return fecha.strftime("%Y-%m-%dT%H:%M:%SUTC")


def recolectar_datos(fecha_inicio, fecha_final, api_key):
    """
    Recolecta datos para un rango de fechas en intervalos de 15 días.
    
    Args:
        fecha_inicio (datetime): Fecha inicial
        fecha_final (datetime): Fecha final
        api_key (str): API key de AEMET
    
    Returns:
        list: Lista de datos climatológicos acumulados
    """
    datos_acumulados = []
    fecha_actual = fecha_inicio
    delta_dias = timedelta(days=15)
    
    while fecha_actual <= fecha_final:
        fecha_intervalo_fin = min(fecha_actual + delta_dias, fecha_final)
        
        fecha_inicio_str = formatear_fecha(fecha_actual)
        fecha_fin_str = formatear_fecha(fecha_intervalo_fin)
        
        print(f"Obteniendo datos de {fecha_inicio_str} a {fecha_fin_str}...")
        datos = obtener_datos(fecha_inicio_str, fecha_fin_str, api_key)
        
        if datos:
            datos_acumulados.extend(datos)
        
        fecha_actual = fecha_intervalo_fin + timedelta(days=1)
    
    return datos_acumulados


def guardar_datos(datos_acumulados, nombre_archivo='datos_climatologicos_anuales.csv'):
    """
    Guarda los datos recolectados en un archivo CSV.
    
    Args:
        datos_acumulados (list): Lista de datos a guardar
        nombre_archivo (str): Nombre del archivo CSV de salida
    """
    if datos_acumulados:
        df = pd.DataFrame(datos_acumulados)
        df.to_csv(nombre_archivo, index=False)
        print(f"Datos guardados en '{nombre_archivo}'")
    else:
        print("No se obtuvieron datos para el año completo.")


def main():
    """Función principal que ejecuta el proceso de recolección de datos."""
    # Configuración inicial
    AÑO = 2024
    api_key = cargar_api_key()
    
    # Obtener rango de fechas
    fecha_inicio, fecha_final = obtener_rango_fechas(AÑO)
    
    # Recolectar datos
    datos_acumulados = recolectar_datos(fecha_inicio, fecha_final, api_key)
    
    # Guardar resultados
    guardar_datos(datos_acumulados)


if __name__ == "__main__":
    main()
