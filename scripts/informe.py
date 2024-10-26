import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar las variables del archivo .env (asegúrate de tener la variable API_KEY en tu .env)
load_dotenv()
api_key = os.getenv('API_KEY')

# Verificar que la API_KEY esté presente
if not api_key:
    print("Error: La API_KEY no se encuentra definida. Asegúrate de que esté en el archivo .env")
    exit()

# Función para obtener los datos de un rango de fechas
def obtener_datos(fecha_inicio, fecha_final):
    URL_BASE = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"
    url = URL_BASE.format(fechaIniStr=fecha_inicio, fechaFinStr=fecha_final) + f"?api_key={api_key}"
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
                    return None
        else:
            print(f"Error al acceder a la API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión a la API: {e}")
        return None

# Definir el año para el cual queremos obtener los datos
año = 2024
fecha_inicio = datetime(año, 1, 1)
fecha_final = datetime(año, 12, 31)

# Lista para acumular datos de cada intervalo de 15 días
datos_acumulados = []

# Iterar cada 15 días dentro del rango del año
delta_dias = timedelta(days=15)
fecha_actual = fecha_inicio

while fecha_actual <= fecha_final:
    # Calcular la fecha de final del intervalo de 15 días
    fecha_intervalo_fin = fecha_actual + delta_dias
    # Ajustar la fecha de final para que no sobrepase el final del año
    if fecha_intervalo_fin > fecha_final:
        fecha_intervalo_fin = fecha_final

    # Formatear las fechas como se requiere por la API (formato ISO)
    fecha_inicio_str = fecha_actual.strftime("%Y-%m-%dT%H:%M:%SUTC")
    fecha_fin_str = fecha_intervalo_fin.strftime("%Y-%m-%dT%H:%M:%SUTC")

    print(f"Obteniendo datos de {fecha_inicio_str} a {fecha_fin_str}...")
    datos = obtener_datos(fecha_inicio_str, fecha_fin_str)
    if datos:
        datos_acumulados.extend(datos)

    # Avanzar al próximo intervalo de 15 días
    fecha_actual = fecha_intervalo_fin + timedelta(days=1)

# Crear un DataFrame con los datos acumulados
if datos_acumulados:
    df = pd.DataFrame(datos_acumulados)
    df.to_csv('datos_climatologicos_anuales.csv', index=False)
    print("Datos de todo el año guardados en 'datos_climatologicos_anuales.csv'")
else:
    print("No se obtuvieron datos para el año completo.")
