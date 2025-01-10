import pandas as pd
from datetime import datetime
import os

# Función personalizada para obtener la segunda fórmula si existe, de lo contrario devuelve la primera
def obtener_formula(text):
    if len(text) > 1:
        if text.split()[0] in ['kg', 'g', 'lb']:
            return text.split()[1]
        else:
            return text.split()[0]
    else:
        return text  # Si no, devuelve la primera

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
        return 'United States'

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
        
def conversion_units(unit, conversion_value):
    # Ajustar valores de 'Conversion Factor 2024' y cambiar 'GHG' de 'g' a 'kg'
    mask = df_final['GHG'] == unit  # Máscara para las filas donde 'GHG' es la unidad indicada
    df_final.loc[mask, 'Conversion Factor 2024'] /= conversion_value  # Dividir entre 1000
    df_final.loc[mask, 'GHG'] = 'kg'  # Cambiar la unidad a 'kg'

    # Cambiar 'GHG/Unit' si comienza con 'g ' a 'kg'
    mask_ghg_unit = df_final['GHG/Unit'].str.startswith(f'{unit} ', na=False)  # Máscara para 'g ' al inicio
    df_final.loc[mask_ghg_unit, 'GHG/Unit'] = df_final['GHG/Unit'].str.replace(f'^{unit} ', 'kg ', regex=True)

# Ruta al archivo de Excel
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(script_dir, "../data_raw/EPA_raw.xlsx")
df_raw = pd.read_excel(ruta, sheet_name='Sheet1', engine='openpyxl')

#GWP
ruta_GWP_values = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
df_GWP = pd.read_excel(ruta_GWP_values, engine='openpyxl')

# Cargar el archivo Excel con labels y URLs
ruta_labels = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
df_labels = pd.read_excel(ruta_labels, engine='openpyxl')

cabeceras = df_raw.columns

df_final = pd.DataFrame(columns=cabeceras)
if 'GHG/Unit' in cabeceras:
    ghg_label='GHG/Unit'
else:
    ghg_label='GHG'
df_final.pop(ghg_label)

# Llenar df_final con los datos de df_raw
for j in range(len(df_raw)):
    fila = df_raw.iloc[j].values.tolist()
    fila = fila[:len(cabeceras)]  # Asegurar que la fila tenga la misma longitud que 'cabeceras'
    df_final.loc[j, cabeceras[:len(fila)]] = fila
print("lineas iniciales", df_final.shape[0])

df_raw[ghg_label] = df_raw[ghg_label].astype(str)
year_dataset = 2024

df_final['Scope'] = df_final['Scope'].astype(str).str.replace(' ', '', regex=False)
df_final.insert(7, "emission_source", None)
df_final['emission_source'] = df_final['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" + df_final['Level 3'].astype(str).str.replace(" ", "_", regex=False)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extraer y limpiar 'emission_target_formula'
df_final['emission_target_formula'] = df_raw[ghg_label].apply(obtener_formula)
df_final['emission_target_formula'] = df_final['emission_target_formula'].replace('nan', None)
# Sustituir 'mmBtu' por una cadena vacía en la columna 'emission_target_formula'
df_final['emission_target_formula'] = df_final['emission_target_formula'].str.replace('mmBtu', '', regex=False)

# Limpiar valores de paréntesis en ambas columnas
df_final[ghg_label] = df_raw[ghg_label]
print("lineas 2", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Cargar el archivo Excel con las formulas y sus respectivas nomenclaturas
ruta_nomen = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
df_nomen = pd.read_excel(ruta_nomen, engine='openpyxl')

df_final['emission_target_formula_aux'] = df_final['emission_target_formula'].str.split().str[-1]
# Crear diccionario de labels y sus URLs
tuplas_nomen = dict(zip(df_nomen['formula'], df_nomen['nomenclatura']))
df_final['emission_target'] = df_final['emission_target_formula_aux'].map(tuplas_nomen)
df_final = df_final.dropna(subset=['emission_target_formula'])

df_final['emission_target_wd'] = df_final['emission_target_formula_aux'].map(tuplas)
print("lineas 3", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extraer 'GHG' del campo 'GHG/Unit'
df_final['GHG/Unit'] = df_final['GHG/Unit'].str.replace(' per unit', '', regex=False)
df_final = df_final[~df_final['GHG/Unit'].str.contains('mmBtu', na=False)]

df_final['GHG'] = df_raw[ghg_label].str.split().str[0]
df_final['GHG'] = df_final['GHG'].replace('nan', None)
# Identificar las filas donde df_final['GHG'] es igual a 'kWh'
filas_a_eliminar = df_final[df_final['GHG'] == 'kWh'].index
conversion_units('g', 1000)
conversion_units('lb', 2.20462)

# Eliminar las filas de esas posiciones
df_final = df_final.drop(filas_a_eliminar)
df_final['GHG_wd'] = df_final['GHG'].map(tuplas)
# Establecer las columnas de validez de fecha
df_final['valid_from'] = datetime(year_dataset, 1, 1, 0, 0, 0).isoformat()
df_final['valid_to'] = datetime(year_dataset, 12, 31, 23, 59, 59).isoformat()
print("lineas 4 ", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Aplicar la función a la columna 'region'
df_final['region'] = df_final['emission_source'].apply(obtener_region)
df_final['region_wd'] = df_final['region'].map(tuplas)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# Renombrar la columna y asegurar tipo string
df_final.columns = df_final.columns.str.strip()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
df_final['GWP'] = df_final.apply(lambda row: calcular_gwp(row, year_dataset,1), axis=1)
df_final[f'Value {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}']  * df_final['GWP']
df_final['GWP'] = df_final.apply(lambda row: calcular_gwp(row, year_dataset,''), axis=1)
df_final['GWP_id'] = df_final.apply(lambda row: id_gwp(row, year_dataset,''), axis=1)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Añadimos CO2e al DataFrame
# Agrupar por 'emission_source'
grupos = df_final.groupby('emission_source')
nuevas_filas = []

# Recorrer cada grupo
for emission_source, grupo in grupos:
    # Sumar 'Conversion Factor 2024'
    suma_conversion = grupo['Conversion Factor 2024'].sum()

    # Crear una nueva fila con los datos de la última fila del grupo
    ultima_fila = grupo.iloc[-1].copy()
    nueva_fila = ultima_fila.copy()
    
    # Modificar la nueva fila
    if pd.notna(ultima_fila['GHG/Unit']):  # Verifica que no sea NaN
        palabras = str(ultima_fila['GHG/Unit']).split(' ')
        if len(palabras) > 1:  # Asegura que haya al menos dos palabras
            palabras[1] = 'CO2e'  # Sustituye la segunda palabra
            nueva_fila['GHG/Unit'] = ' '.join(palabras)
    else:
        nueva_fila['GHG/Unit'] = 'kg CO2e'  # Valor por defecto si 'GHG/Unit' es NaN
    
    nueva_fila['Conversion Factor 2024'] = suma_conversion

    # Calcular el nuevo valor para 'emission_target_formula'
    nueva_fila['emission_target_formula'] = 'CO2e'

    # Mapear la nueva fórmula en 'emission_target' y 'emission_target_wd'
    nueva_fila['emission_target'] = tuplas_nomen.get('CO2e', None)
    nueva_fila['emission_target_wd'] = tuplas.get('CO2e', None)

    # Calcular GWP
    nueva_fila['GWP'] = None
    nueva_fila['GWP_id'] = None

    # Calcular el nuevo valor para 'Value {year_dataset}'
    nueva_fila[f'Value {year_dataset}'] = nueva_fila['Conversion Factor 2024']

    # Agregar la nueva fila al DataFrame original antes de cambiar de 'emission_source'
    nuevas_filas.append((grupo.index[-1], nueva_fila))

# Insertar las nuevas filas en el DataFrame original
for index, fila in sorted(nuevas_filas, reverse=True):
    # Paso 1: Concatenar las filas
    df_final = pd.concat([df_final.iloc[:index + 1], pd.DataFrame([fila]), df_final.iloc[index + 1:]]).reset_index(drop=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Eliminar la columna emission_target_formula_aux
df_final = df_final.drop(columns=['emission_target_formula_aux'])

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Si se añadió 'id' manualmente en 'cabeceras', generar valores de ID
if 'id' in df_final.columns:
    df_final['id'] = range(1, len(df_final) + 1)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Guardar en Excel
ruta_final = os.path.join(script_dir, f"../data/Conversion_Factor_{year_dataset}.xlsx")
df_final.to_excel(ruta_final, index=False)
print("lineas finales", df_final.shape[0])
