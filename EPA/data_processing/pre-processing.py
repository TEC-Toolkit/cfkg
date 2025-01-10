import re
import pandas as pd
import warnings
import os
import numpy as np
# Función para quitar texto entre paréntesis
def limpiar_parentesis(text):
    if '(' in text:
        return text.split('(')[0].strip()
    else:
        return text.strip()

# Ignorar advertencias específicas
warnings.filterwarnings("ignore")

# Ruta al archivo de Excel
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(script_dir, "../data_raw/ghg-emission-factors-hub-2024.xlsx")
df_raw = pd.read_excel(ruta, sheet_name='Emission Factors Hub', engine='openpyxl')

# ---------------------------------------------------------------------------------------------------------------------------------
# PROCESAMIENTO DE TABLA 1 (scope 1)
df = df_raw.iloc[15:90, 2:]  # Extraer la tabla 1
df.columns = df_raw.iloc[14, 2:]  # Establecer cabecera
df = df.reset_index(drop=True)

# Inicializar `ghg_units` con las unidades GHG/Unit
ghg_units = df_raw.iloc[15, 2:].tolist()

# Crear DataFrame final vacío
df_final = pd.DataFrame(columns=['id', 'Scope', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 
                                'Column Text', 'UOM', 'GHG/Unit', 'Conversion Factor 2024'])

# Variable temporal para almacenar categoría actual de Level 2
current_level_2 = None

# Procesar filas de la tabla 1
for index, row in df.iterrows():
    if pd.isna(row.iloc[0]):  # Si la fila comienza vacía
        ghg_units = row.iloc[1:].tolist()  # Actualizar `ghg_units`
    elif pd.notna(row.iloc[0]) and row.iloc[1:].isna().all():
        current_level_2 = row.iloc[0]  # Actualizar categoría Level 2
    else:
        # Crear filas para cada valor en `GHG/Unit`
        if pd.notna(row.iloc[0]):
            for i, ghg_unit in enumerate(ghg_units):
                conversion_factor = row.iloc[i + 1] if pd.notna(row.iloc[i + 1]) else None
                new_row = {
                    'id': None,
                    'Scope': "Scope 1",
                    'Level 1': "Stationary Combustion",
                    'Level 2': current_level_2 if current_level_2 else "",
                    'Level 3': row.iloc[0],
                    'Level 4': None,
                    'Column Text': None,
                    'UOM': 'Metric Tons',
                    'GHG/Unit': ghg_unit,
                    'Conversion Factor 2024': conversion_factor
                }
                df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs únicos
df_final['id'] = range(1, len(df_final) + 1)
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 3 (scope 1)
df3 = df_raw.iloc[123:235, 2:]  # Extraer la tabla 3
df3.columns = df_raw.iloc[122, 2:]
df3 = df3.loc[:, ~df3.columns.isna()]  # Eliminar columnas vacías

# Variables temporales para almacenar categorías actuales
current_level_1 = None
current_level_2 = 'On-Road Gasoline Vehicles'
column_text = None
# Obtener último ID usado
last_id = df_final['id'].max()

# Procesar filas de la tabla 3 y añadirlas directamente a df_final
for index, row in df3.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        # Dividir 'Vehicle Type' en Level 1 y Level 2
        try:
            column_text, current_level_1 = row['Vehicle Type'].split(' ', 1)
        except ValueError:
            column_text = row['Vehicle Type']
            current_level_1 = ""

    level_3 = row.get('Model Year')
    
    # Crear filas para cada unidad GHG/Unit
    for ghg_unit, conversion_factor in zip(df3.columns[-2:], row[-2:]):
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        new_row = {
            'id': df_final['id'].max() + 1,
            'Scope': "Scope 1",
            'Level 1': current_level_1,
            'Level 2': current_level_2,
            'Level 3': level_3,
            'Level 4': None,
            'Column Text': column_text,
            'UOM': 'Metric Tons',
            'GHG/Unit': ghg_unit,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 4 (scope 1)
# Crear una lista para almacenar las filas transformadas
df4 = df_raw.iloc[241:275, 2:]  # Extraer la tabla 3
df4.columns = df_raw.iloc[240, 2:]
df4 = df4.loc[:, ~df4.columns.isna()]  # Eliminar columnas vacías

level_1 = None
level_2 = 'On-Road Diesel and Alternative Fuel Vehicles'
level_3 = None
column_text = None
for index, row in df4.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
    if pd.notna(row.get('Fuel Type')):
        column_text = row.get('Fuel Type')
    if pd.notna(row.get('Model Year')):
        level_3 = row.get('Model Year')
    else:
        level_3 = ''
    # Crear filas para cada unidad GHG/Unit
    for ghg_unit, conversion_factor in zip(df4.columns[-2:], row[-2:]):
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        new_row = {
            'id': df_final['id'].max() + 1,
            'Scope': "Scope 1",
            'Level 1': level_1,
            'Level 2': level_2,
            'Level 3': level_3,
            'Level 4': None,
            'Column Text': column_text,
            'UOM': 'Metric Tons',
            'GHG/Unit': ghg_unit,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 5 (scope 1)
# Crear una lista para almacenar las filas transformadas
df5 = df_raw.iloc[282:322, 2:]  # Extraer la tabla 5
df5.columns = df_raw.iloc[281, 2:]
df5 = df5.loc[:, ~df5.columns.isna()]  # Eliminar columnas vacías

level_1 = None
level_2 = 'Non-Road Vehicles'
column_text = None

for index, row in df5.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
    if pd.notna(row.get('Fuel Type')):
        column_text = row.get('Fuel Type')
    # Crear filas para cada unidad GHG/Unit
    for ghg_unit, conversion_factor in zip(df5.columns[-2:], row[-2:]):
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        new_row = {
            'id': df_final['id'].max()+1,
            'Scope': "Scope 1",
            'Level 1': level_1,
            'Level 2': level_2,
            'Level 3': None,
            'Level 4': None,
            'Column Text': column_text,
            'UOM': 'Metric Tons',
            'GHG/Unit': ghg_unit,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
#TABLA 6 (Scope 2)
# Extraer y limpiar la tabla
df6 = df_raw.iloc[330:359, 1:7]  # Ajustar el rango de filas para incluir la tabla correcta
columns_primary = df_raw.iloc[329, 1:7]  # Encabezados principales
columns_secondary = df_raw.iloc[330, 1:7]  # Encabezados secundarios
df6 = df6.loc[:, ~df6.columns.isna()]  # Eliminar columnas vacías
df6.columns = pd.MultiIndex.from_tuples(zip(columns_primary, columns_secondary))

level_2 = None
level_3 = None
i=0
for index, row in df6.iterrows():
    i+=1
    if i > 1:
        if pd.notna(row.get(('eGRID Subregion Name', np.nan))):  # Usa np.nan en la tupla
            level_3 = row[('eGRID Subregion Name', np.nan)]
        secondary_headers = df6.columns.get_level_values(1)  # Nivel secundario
        
        for ghg_unit, conversion_factor in zip(secondary_headers[~pd.isna(secondary_headers)][-3:], row[-3:]):            
            ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
            new_row = {
                'id': df_final['id'].max()+1,
                'Scope': "Scope 2",
                'Level 1': "Electricity",
                'Level 2': level_2,
                'Level 3': level_3,
                'Level 4': None,
                'Column Text': 'Total Output Emission Factors',
                'UOM': 'Metric Tons',
                'GHG/Unit': ghg_unit,
                'Conversion Factor 2024': conversion_factor
            }
            df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
#TABLA 6 PT 2 (Scope 2)
df6 = pd.concat([
    df_raw.iloc[330:359, 1:4],  # Columnas 1 a 4
    df_raw.iloc[330:359, 7:11]  # Columnas 8 a 10
], axis=1)

# Asignar encabezados principales y secundarios
columns_primary = pd.concat([
    df_raw.iloc[329, 1:4],  # Encabezados principales (columnas 1 a 4)
    df_raw.iloc[329, 7:11]  # Encabezados principales (columnas 8 a 10)
], axis=0)
columns_secondary = pd.concat([
    df_raw.iloc[330, 1:4],  # Encabezados secundarios (columnas 1 a 4)
    df_raw.iloc[330, 7:11]  # Encabezados secundarios (columnas 8 a 10)
], axis=0)

# Eliminar columnas vacías y crear MultiIndex
df6 = df6.loc[:, ~df6.columns.isna()]  # Eliminar columnas con encabezados NaN
df6.columns = pd.MultiIndex.from_tuples(zip(columns_primary, columns_secondary))  # Crear MultiIndex
level_2 = None
level_3 = None
i=0
for index, row in df6.iterrows():
    i+=1
    if i > 1:
        if pd.notna(row.get(('eGRID Subregion Name', np.nan))):  # Usa np.nan en la tupla
            level_3 = row[('eGRID Subregion Name', np.nan)]
        secondary_headers = df6.columns.get_level_values(1)  # Nivel secundario
        
        for ghg_unit, conversion_factor in zip(secondary_headers[~pd.isna(secondary_headers)][-3:], row[-3:]):
            ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
            new_row = {
                'id': df_final['id'].max() + 1,
                'Scope': "Scope 2",
                'Level 1': "Electricity",
                'Level 2': level_2,
                'Level 3': level_3,
                'Level 4': None,
                'Column Text': 'Non-Baseload Emission Factors',
                'UOM': 'Metric Tons',
                'GHG/Unit': ghg_unit,
                'Conversion Factor 2024': conversion_factor
            }
            df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 8 (scope 3)
# Crear una lista para almacenar las filas transformadas
df8 = df_raw.iloc[411:418, 2:]  # Extraer la tabla 8
df8.columns = df_raw.iloc[410, 2:]
df8 = df8.loc[:, ~df8.columns.isna()]  # Eliminar columnas vacías

level_1 = None
level_2 = 'Downstream Transportation and Distribution'

for index, row in df8.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
    # Crear filas para cada unidad GHG/Unit
    for ghg_unit, conversion_factor in zip(df8.columns[-4:], row[1:4]):
        # Extraer la unidad completa de la última columna
        unit = row[df8.columns[-1]]  # Seleccionar toda la celda correspondiente a la última columna
        # Extraer el texto dentro de los paréntesis
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        # Crear nueva fila
        new_row = {
            'id': df_final['id'].max() + 1,
            'Scope': "Scope 3",
            'Level 1': level_1,
            'Level 2': level_2,
            'Level 3': None,
            'Level 4': None,
            'Column Text': None,
            'UOM': unit,
            'GHG/Unit': ghg_unit,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 9 (scope 3)
df9 = df_raw.iloc[425:486, 2:]  # Extraer la tabla 8
df9.columns = df_raw.iloc[424, 2:]
df9 = df9.loc[:, ~df9.columns.isna()]  # Eliminar columnas vacías
#print(df9)
level_1 = None
level_2 = 'End-of-Life Treatment of Sold Products'
column_text = None
for index, row in df9.iterrows():
    if pd.notna(row.get('Material')):
        column_text = row.get('Material')
    # Crear filas para cada unidad GHG/Unit
    for level_1, conversion_factor in zip(df9.columns[-6:], row[1:]):
        level_1 = level_1[:-1]
        #print(f'{level_1}\t{conversion_factor}')
        # Crear nueva fila
        new_row = {
            'id': df_final['id'].max() + 1,
            'Scope': "Scope 3",
            'Level 1': level_1,
            'Level 2': level_2,
            'Level 3': None,
            'Level 4': None,
            'Column Text': column_text,
            'UOM': 'Metric Tons',
            'GHG/Unit': None,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLA 10 (scope 3)
# Crear una lista para almacenar las filas transformadas
df10 = df_raw.iloc[493:505, 2:]  # Extraer la tabla 8
df10.columns = df_raw.iloc[492, 2:]
df10 = df10.loc[:, ~df10.columns.isna()]  # Eliminar columnas vacías

level_1 = None
level_2 = 'Employee Commuting'
level_3 = None
for index, row in df10.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
        if level_1[-2] == ' ' and level_1[-1].isalpha():
            level_1 = level_1[:-2]
        if ' - ' in level_1:
            div = level_1.split('-', maxsplit=1)  # Divide en dos partes como máximo
            level_1 = div[0]
            level_3 = div[1]
        else:
            level_3 = None
    # Crear filas para cada unidad GHG/Unit
    for ghg_unit, conversion_factor in zip(df10.columns[-4:], row[1:4]):
        # Extraer la unidad completa de la última columna
        unit = row[df10.columns[-1]]  # Seleccionar toda la celda correspondiente a la última columna
        # Extraer el texto dentro de los paréntesis
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        # Crear nueva fila
        new_row = {
            'id': df_final['id'].max() + 1,
            'Scope': "Scope 3",
            'Level 1': level_1,
            'Level 2': level_2,
            'Level 3': level_3,
            'Level 4': None,
            'Column Text': None,
            'UOM': unit,
            'GHG/Unit': ghg_unit,
            'Conversion Factor 2024': conversion_factor
        }
        df_final = pd.concat([df_final, pd.DataFrame([new_row])], ignore_index=True)

# Asignar IDs continuando desde el último ID
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# EXPORTACIÓN
# Ordenar por ID y exportar a Excel
df_final = df_final.sort_values(by='id').reset_index(drop=True)
ruta_final = os.path.join(script_dir, f"../data_raw/EPA_raw.xlsx")
df_final.to_excel(ruta_final, index=False)