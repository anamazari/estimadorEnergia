from flask import Flask, render_template, request
import csv
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os

app = Flask(__name__) #Se crea una instancia de la clase Flask y se le pasa __name__, que es una variable especial de Python que representa el nombre del módulo actual. 

def cargar_datos_renovables(ruta_csv):
    datos=[]
    try:
        with open(ruta_csv, mode='r', encoding='utf-8') as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            for fila in lector:
                datos.append({
                    'entity': fila['Entity'],
                    'code': fila['Code'],
                    'year': int(fila['Year']),
                    'renewables': float(fila['Renewables (% equivalent primary energy)'])
                })
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return datos

RUTA_CSV = 'static/archivo/data.csv'
datos_renovables = cargar_datos_renovables(RUTA_CSV)

DATA_DIR = 'static/archivo/'
FILES = {
    "Wind" : ("08 wind-generation.csv", "Electricity from wind (TWh)"),
    "Solar" : ("12 solar-energy-consumption.csv", "Electricity from solar (TWh)"),
    "Hydropower" : ("05 hydropower-consumption.csv", "Electricity from hydro (TWh)"),
    "Biofuels" : ("16 biofuel-production.csv", "Biofuels Production - TWh - Total"),
    "Geothermal" : ("17 installed-geothermal-capacity.csv", "Geothermal Capacity")
}

def load_data():
    data={}
    for key, (file_name, column) in FILES.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_production = df[column].sum()
            data[key] = total_production
    return data

@app.route('/', methods=['GET', 'POST'])#@app.route('/'): Este es un decorador que se usa para vincular una URL (en este caso, la raíz '/') con una función. La función index() se ejecutará cuando un usuario acceda a la raíz de la aplicación.

def index():
    porcentaje_renovable = None
    error = None

    #-------------------------------------------- GRAFICA DE BARRAS -------------------------------------------

    data = load_data()
    plt.subplots(figsize=(3,2))
    df = pd.DataFrame(list(data.items()), columns=['Fuente', 'Producción (TWh)'])

    fig, ax = plt.subplots(figsize=(5,4))
    ax.bar(df['Fuente'], df['Producción (TWh)'], color=['lightgreen', 'gray', 'lightgreen', 'gray', 'lightgreen'])

    ax.set_title('Producción de Energía Renovable por Fuente', fontsize=12)
    ax.set_xlabel('Fuente de Energía', fontsize=12)
    ax.set_ylabel('Producción (TWh)', fontsize=12)

    #------------------------------------- Convertimos la gráfica en imagen -----------------------------------
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf-8')
    #----------------------------------------------------------------------------------------------------------

    
    if request.method == 'POST':
        try:
            consumo_total = float(request.form['consumo_total'])
            if consumo_total <= 0:
                error = "El consumo total debe ser un valor positivo."
            else:
                produccion_total_renovable = sum(energia['renewables'] for energia in datos_renovables)
                if produccion_total_renovable >= consumo_total:
                    porcentaje_renovable = (consumo_total/produccion_total_renovable)*100
                else:
                    porcentaje_renovable = 100
            
        except ValueError:
            error ="Por Favor ingrese un valor válido para el consumo total."
    
    return render_template('index.html',porcentaje_renovable = porcentaje_renovable, error = error, graph_url = graph_url)

if __name__ == '__main__':
    app.run(debug=True)#Este bloque verifica si el script está siendo ejecutado directamente (y no importado como un módulo en otro programa). Si es así, ejecuta el servidor de desarrollo de Flask con app.run(debug=True)