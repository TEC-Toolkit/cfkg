from datetime import datetime
import re
import pandas as pd
import os

def limpiar_parentesis(text):
    if not isinstance(text, str):  # Verificar si no es una cadena
        return text  # Devolver el valor original si no es una cadena
    if '(' in text:
        return text.split('(')[0].strip()  # Toma la parte antes del paréntesis y elimina espacios
    else:
        return text.strip()  # Si no hay paréntesis, devuelve el texto original sin espacios adicionales

def calcular_gwp(row, year_dataset):
    #filtrar por año
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # duplas
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["value"]))
    #print(row)
    return gwp_dict.get(row["emission_target_formula"])

def id_gwp(row, year_dataset):
    #filtrar por año
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # duplas
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["id"]))
    #print(row)
    return gwp_dict.get(row["emission_target_formula"])

# Función para extraer la parte después del guion bajo si comienza con un número
def modificar_column_text(text):
    if pd.notna(text) and re.match(r'^\d', text):  # Verifica si no es NaN y comienza con un número
        partes = text.split('_', 1)  # Divide solo una vez por '_'
        return partes[1] if len(partes) > 1 else text  # Retorna la parte después de '_' si existe
    return text  # Retorna el texto original si no cumple la condición

def kilotonne_to_kg(df, year_dataset):
    # Máscara para identificar las filas donde 'GHG' es 'kilotonne'
    mask = df['GHG'] == 'kilotonne'
    # Reemplazar 'kilotonne' por 'kg' en la columna 'GHG'
    df.loc[mask, 'GHG'] = 'kg'
    conversion_column = f'Conversion Factor {year_dataset}'
    df.loc[mask, conversion_column] = df.loc[mask, conversion_column] * 1e6

def definir_scope(row):
    """
    Función para definir el scope en función del valor de 'Level 1'.

    - Si 'Level 1' es "Agriculture" o "Industrial Processes and Other Product Use" -> scope1.
    - Si 'Level 1' es "Energy" -> scope2.
    - Cualquier otro valor -> scope3.
    """
    if row['Level 1'] in ['Agriculture', 'Industrial Processes and Other Product Use']:
        return 'Scope1'
    elif row['Level 1'] == 'Energy':
        return 'Scope2'
    else:
        return 'Scope3'

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

# Filtrar y guardar la información por año
for year in years:
    try:
        df_year = df[df['Year'] == year].copy()  # Crear una copia del DataFrame filtrado
        #-------------------------------------------------------------------------------------------
        # Renombrar columnas
        rename_cols = {
            'Pollutant': 'emission_target',
            'Sector': 'Level 1',
            'Source': 'Level 2',
            'Fuel Name': 'Level 3',
            'NFR Code': 'Column Text',
            'Activity Units': 'UOM',
            'Units': 'GHG',
            'Emission Factor': f'Conversion Factor {year}'
        }
        print
        df_year.rename(columns=rename_cols, inplace=True)
        #-------------------------------------------------------------------------------------------
        # Aplicar la función a la columna 'Column Text'
        df_year['Column Text'] = df_year['Column Text'].apply(modificar_column_text)
        #-------------------------------------------------------------------------------------------
        # Cargar las fórmulas y mapear
        ruta_nomen = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
        df_nomen = pd.read_excel(ruta_nomen, engine='openpyxl')
        tuplas_nomen = dict(zip(df_nomen['nomenclatura'], df_nomen['formula']))

        df_year['emission_target_formula'] = df_year['emission_target'].map(tuplas_nomen)
        #-------------------------------------------------------------------------------------------
        # Crear nuevas columnas
        df_year['emission_source'] = (
            df_year['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" +
            df_year['Level 3'].astype(str).str.replace(" ", "_", regex=False)
        )
        #-------------------------------------------------------------------------------------------
        # Eliminar filas donde 'UOM' esté vacío
        df_year = df_year[df_year['UOM'].str.strip() != '']  # Elimina filas donde 'UOM' es una cadena vacía o espacios
        df_year = df_year.dropna(subset=['UOM'])  # También elimina las filas con NaN en 'UOM'
        #-------------------------------------------------------------------------------------------
        # Aplicar la función al DataFrame
        kilotonne_to_kg(df_year, year)
        df_year['GHG/Unit'] = df_year['GHG'].astype(str) + " " + df_year['emission_target_formula']
        #-------------------------------------------------------------------------------------------
        # Cargar labels y URLs
        ruta_labels = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
        df_labels = pd.read_excel(ruta_labels, engine='openpyxl')
        tuplas = dict(zip(df_labels['label'], df_labels['label_url']))
        df_year['UOM_wd'] = df_year['UOM'].apply(limpiar_parentesis).map(tuplas)
        df_year['GHG_wd'] = df_year['GHG'].map(tuplas)
        df_year['emission_target_wd'] = df_year['emission_target_formula'].map(tuplas)
        #-------------------------------------------------------------------------------------------
        df_year['region'] = 'United Kingdom'
        df_year['region_wd'] = df_year['region'].map(tuplas)
        #-------------------------------------------------------------------------------------------
        # Agregar fechas y columnas adicionales
        df_year['valid_from'] = datetime(year, 1, 1, 0, 0, 0).isoformat()
        df_year['valid_to'] = datetime(year, 12, 31, 23, 59, 59).isoformat()
        #-------------------------------------------------------------------------------------------
        # Otras operaciones
        # Aplicar la función al DataFrame
        df_year['Scope'] = df_year.apply(definir_scope, axis=1)
        df_year['Level 4'] = None
        df_year = df_year[df_year['emission_target'] != 'Bio-Carbon']

        #GWP
        ruta_GWP_values = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
        df_GWP = pd.read_excel(ruta_GWP_values, engine='openpyxl')

        df_year['GWP'] = df_year.apply(lambda row: calcular_gwp(row, year), axis=1)
        df_year[f'Value {year}'] = df_year[f'Conversion Factor {year}']  / df_year['GWP']
        df_year['GWP_id'] = df_year.apply(lambda row: id_gwp(row, year), axis=1)
        #-------------------------------------------------------------------------------------------
        # Generar IDs únicos
        df_year['id'] = range(1, len(df_year) + 1)
        #-------------------------------------------------------------------------------------------
        # Reordenar columnas
        nuevo_orden = [
            'id', 'Scope', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Column Text',
            'emission_source', 'UOM', 'UOM_wd', 'GHG/Unit', 'emission_target_formula',
            'emission_target', 'emission_target_wd','GHG', 'GHG_wd',
            'valid_from', 'valid_to', 'region', 'region_wd', f'Conversion Factor {year}', 
            f'Value {year}', 'GWP', 'GWP_id'
        ]
        df_year = df_year[nuevo_orden]
        #-------------------------------------------------------------------------------------------
        # Guardar el archivo Excel
        output_file = os.path.join(script_dir, f"../data/Conversion_Factor_{year}.xlsx")
        df_year.to_excel(output_file, index=False)
        print(f"Archivo guardado: Conversion_Factor_{year}.xlsx")
    except Exception as e:
        print(f"Error al procesar el año {year}: {e}")