import pandas as pd
from datetime import datetime
import os

def obtener_formula(text):
    formulas = text.split(' per ')[0].strip()  # Toma lo que esté antes de 'per'
    if len(formulas) > 1:
        if 'kg' in formulas:
            formulas = formulas.replace('kg', '').strip()  # Remueve 'kg' si está presente
        return formulas
    else:
        return formulas[0]  # Si no, devuelve la primera

# Función para quitar net/gross CV para poder poner la URL de wikidata posteriormente
def limpiar_parentesis(text):
    if '(' in text:
        return text.split('(')[0].strip()  # Toma la parte antes del paréntesis y elimina espacios
    else:
        return text.strip()  # Si no hay paréntesis, devuelve el texto original sin espacios adicionales

# Modificar la columna 'region' basada en 'emission_source'
def obtener_region(emission_source):
    if emission_source.startswith('Hotel_stay'):
        # Eliminar el prefijo 'Hotel_stay_' y reemplazar '_' por espacios
        return emission_source.replace('Hotel_stay_', '').replace('_', ' ')
    else:
        return 'United Kingdom'

def nomenclatura(formula):
    if formula is None or pd.isna(formula):  # Verifica si el valor es None o NaN
        return None
    if 'of' in formula:  # Comprueba si 'of' está en la fórmula
        formula1, formula2 = formula.split(' of ')  # Divide la cadena en dos partes
        # Realiza el mapeo usando el diccionario tuplas_nomen
        formula1_mapped = tuplas_nomen.get(formula1.strip(), formula1.strip())
        formula2_mapped = tuplas_nomen.get(formula2.strip(), formula2.strip())
        result = f"{formula1_mapped} of {formula2_mapped}"
        return result
    else:
        # Mapea directamente si la fórmula no contiene 'of'
        return tuplas_nomen.get(formula.strip(), formula.strip())

def calcular_gwp(row, year_dataset, valor):
    #filtrar por año
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # duplas
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["value"]))
    #print(row)
    return gwp_dict.get(row["emission_target_formula_aux"], valor)

def id_gwp(row, year_dataset, valor):
    #filtrar por año
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # duplas
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["id"]))
    #print(row)
    return gwp_dict.get(row["emission_target_formula_aux"], valor)

# Ruta al directorio de los archivos Excel
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(script_dir, "../data_raw/ghg-conversion-factors-2022-flat-format.xlsx")
# Leer el archivo Excel
df_raw = pd.read_excel(ruta, sheet_name='Factors by Category', engine='openpyxl')
# Realizar las operaciones que desees en cada DataFrame

i = 0
cabeceras = []
while 'Scope' not in cabeceras:
    i += 1
    cabeceras = df_raw.iloc[i].tolist()
df_raw = pd.read_excel(ruta, sheet_name='Factors by Category', engine='openpyxl', header=i+1)

# Verificar si no hay una columna de ID y, si no existe, añadirla a 'cabeceras'
if not any(col.lower() == 'id' for col in cabeceras):
    cabeceras.insert(0, 'id')
df_final = pd.DataFrame(columns=cabeceras)
if 'GHG/Unit' in cabeceras:
    ghg_label='GHG/Unit'
else:
    ghg_label='GHG'
    
df_final.pop(ghg_label)

# Llenar df_final con los datos de df_raw
for j in range(len(df_raw)):
    fila = df_raw.iloc[j].values.tolist()
    if 'id' in df_final.columns:  # Si 'id' fue añadido manualmente
        fila.insert(0, None)  # Inserta None al inicio para alinearlo con 'id'
    fila = fila[:len(cabeceras)]  # Asegurar que la fila tenga la misma longitud que 'cabeceras'
    df_final.loc[j, cabeceras[:len(fila)]] = fila
print("lineas iniciales", df_final.shape[0])

df_raw[ghg_label] = df_raw[ghg_label].astype(str)
column_name = [col for col in df_raw.columns if 'GHG Conversion Factor' in col][0]
year_dataset = int(column_name.split()[-1])

df_final['Scope'] = df_final['Scope'].astype(str).str.replace(' ', '', regex=False)
df_final.insert(7, "emission_source", None)
df_final['emission_source'] = df_final['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" + df_final['Level 3'].astype(str).str.replace(" ", "_", regex=False)

# Cargar el archivo Excel con labels y URLs
ruta_labels = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
df_labels = pd.read_excel(ruta_labels, engine='openpyxl')
df_labels['label_url'] = df_labels['label_url'].str.strip()

# Crear diccionario de labels y sus URLs
tuplas = dict(zip(df_labels['label'], df_labels['label_url']))

# Extraer los valores de URL para las columnas en df_final que terminan en '_wd'
for col in df_final.columns:
    if col.endswith('_wd'):
        # Obtener la columna base sin '_wd' y reemplazarla por sus URLs del diccionario
        base_col = col[:-3]
        df_final[col] = df_final[base_col].map(tuplas).fillna('-')

# ---------------------- Otras transformaciones ----------------------

df_final['UOM'] = df_final['UOM'].fillna('').astype(str)
df_final['UOM'] = df_final['UOM'].apply(limpiar_parentesis)
print("lineas 1 ", df_final.shape[0])

# Crear la columna 'UOM_wd' mapeando los valores de 'UOM' al diccionario de labels y URLs (tuplas)
df_final['UOM_wd'] = df_final['UOM'].map(tuplas)
# Reordenar las columnas para que 'UOM_wd' aparezca justo después de 'UOM'
columnas = list(df_final.columns)
indice_uom = columnas.index('UOM')
# Insertar 'UOM_wd' después de 'UOM'
columnas.insert(indice_uom + 1, columnas.pop(columnas.index('UOM_wd')))
df_final = df_final[columnas]

# Extraer y limpiar 'emission_target_formula'
df_final['emission_target_formula'] = df_raw[ghg_label].apply(obtener_formula)
df_final['emission_target_formula'] = df_final['emission_target_formula'].apply(lambda x: x.replace('kg', '').strip() if isinstance(x, str) else x)
df_final['emission_target_formula'] = df_final['emission_target_formula'].replace('nan', None)
# Limpiar valores de paréntesis en ambas columnas
df_final['emission_target_formula'] = df_final['emission_target_formula'].str.replace("(Net CV)", "", regex=False).str.replace("(Gross CV)", "", regex=False).str.replace("(net)", "", regex=False).str.replace("kWh ", "kWh", regex=False)
df_final[ghg_label] = df_raw[ghg_label].str.replace("(Net CV)", "", regex=False).str.replace("(Gross CV)", "", regex=False).str.replace("(net)", "", regex=False)

# Cargar el archivo Excel con las formulas y sus respectivas nomenclaturas
ruta_nomen = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
df_nomen = pd.read_excel(ruta_nomen, engine='openpyxl')
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
df_final['emission_target_formula_aux'] = df_final['emission_target_formula'].str.split().str[-1]
# Crear diccionario de labels y sus URLs
tuplas_nomen = dict(zip(df_nomen['formula'], df_nomen['nomenclatura']))
df_final['emission_target'] = df_final['emission_target_formula'].apply(nomenclatura)
df_final = df_final.dropna(subset=['emission_target_formula'])

df_final['emission_target_wd'] = df_final['emission_target_formula'].map(tuplas)
print("lineas 2 ", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extraer 'GHG' del campo 'GHG/Unit'
df_final['GHG'] = df_raw[ghg_label].str.split().str[0]
df_final['GHG'] = df_final['GHG'].replace('nan', None).str.replace(' per unit', '', regex=False)
# Identificar las filas donde df_final['GHG'] es igual a 'kWh'
filas_a_eliminar = df_final[df_final['GHG'] == 'kWh'].index
# Eliminar las filas de esas posiciones
df_final = df_final.drop(filas_a_eliminar)
df_final['GHG_wd'] = df_final['GHG'].map(tuplas)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Establecer las columnas de validez de fecha
df_final['valid_from'] = datetime(year_dataset, 1, 1, 0, 0, 0).isoformat()
df_final['valid_to'] = datetime(year_dataset, 12, 31, 23, 59, 59).isoformat()
print("lineas 4 ", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Aplicar la función a la columna 'region'
df_final['region'] = df_final['emission_source'].apply(obtener_region)
df_final['region_wd'] = df_final['region'].map(tuplas)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
df_final = df_final.rename(columns={f'GHG Conversion Factor {year_dataset}': f'Conversion Factor {year_dataset}'})
# Asegurarse de que los valores son de tipo string para usar .str.replace() y luego convertir a numérico
df_final[f'Conversion Factor {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}'].astype(str)
df_final[f'Conversion Factor {year_dataset}'] = pd.to_numeric(df_final[f'Conversion Factor {year_dataset}'].str.replace(',', '', regex=False), errors='coerce')
print("lineas 5 ", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Eliminar filas con NaN en 'Conversion Factor {year_dataset}'
df_final = df_final.dropna(subset=[f'Conversion Factor {year_dataset}'])
print("lineas 6 ", df_final.shape[0])
# Mover 'Conversion Factor {year_dataset}' a la última posición
columna_conversion_factor = f'Conversion Factor {year_dataset}'
columnas = [col for col in df_final.columns if col != columna_conversion_factor] + [columna_conversion_factor]
df_final = df_final[columnas]
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Renombrar la columna y asegurar tipo string
df_final.columns = df_final.columns.str.strip()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#GWP
ruta_GWP_values = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
df_GWP = pd.read_excel(ruta_GWP_values, engine='openpyxl')

df_final['GWP'] = df_final.apply(lambda row: calcular_gwp(row, year_dataset,1), axis=1)
df_final[f'Value {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}']  / df_final['GWP']
df_final['GWP'] = df_final.apply(lambda row: calcular_gwp(row, year_dataset,''), axis=1)
df_final['GWP_id'] = df_final.apply(lambda row: id_gwp(row, year_dataset,''), axis=1)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Si se añadió 'id' manualmente en 'cabeceras', generar valores de ID
if 'id' in df_final.columns and df_final['id'].isnull().all():
    df_final['id'] = range(1, len(df_final) + 1)

# Eliminar la columna emission_target_formula_aux
df_final = df_final.drop(columns=['emission_target_formula_aux'])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Guardar en Excel
ruta_final = os.path.join(script_dir, f"../data/v3/Conversion_Factor_{year_dataset}_v3.csv")
df_final.to_csv(ruta_final, index=False)
print("lineas finales", df_final.shape[0])
