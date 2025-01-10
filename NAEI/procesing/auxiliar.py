from datetime import datetime
import pandas as pd
import os

def limpiar_parentesis(text):
    if not isinstance(text, str):  # Verificar si no es una cadena
        return text  # Devolver el valor original si no es una cadena
    if '(' in text:
        return text.split('(')[0].strip()  # Toma la parte antes del paréntesis y elimina espacios
    else:
        return text.strip()  # Si no hay paréntesis, devuelve el texto original sin espacios adicionales

script_dir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(script_dir, "../data_raw/export.xlsx")

# Leer el archivo Excel
try:
    df = pd.read_excel(ruta, sheet_name='export', engine='openpyxl')
except Exception as e:
    print(f"Error al leer el archivo Excel: {e}")
    exit()

# Verificar si la columna de años existe
if 'Year' not in df.columns:
    print(f"Error: La columna 'Year' no existe en el archivo Excel.")
    exit()

# Obtener los años únicos
years = df['Year'].unique()

# Lista para almacenar los valores únicos de UOM
uom_unicos = set()

# Filtrar y guardar la información por año
for year in years:
    try:
        df_year = df[df['Year'] == year].copy()  # Crear una copia del DataFrame filtrado
        
        # Renombrar columnas
        rename_cols = {
            'Pollutant': 'emission_target',
            'Sector': 'Level 1',
            'Source': 'Level 2',
            'Fuel Name': 'Level 3',
            'NFR Code': 'Column Text',
            'Activity Units': 'UOM',
            'Units': 'GHG'
        }
        df_year.rename(columns=rename_cols, inplace=True)
        
        # Recoger los valores únicos de la columna UOM del año actual
        uom_unicos.update(df_year['UOM'].dropna().unique())
        print(df_year.columns)
    except Exception as e:
        print(f"Error al procesar el año {year}: {e}")
"""
# Imprimir los valores únicos de UOM, uno por línea
print("Valores únicos de UOM:")
for uom in sorted(uom_unicos):
    print(uom)
"""
