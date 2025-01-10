import pandas as pd
import os
import requests

def search_wikidata(term):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "language": "en",  # Puedes cambiar el idioma si es necesario
        "format": "json",
        "search": term
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Verificar si hay resultados en la búsqueda
        if data['search']:
            # Tomar el primer resultado y devolver la URL
            entity_id = data['search'][0]['id']
            return f"https://www.wikidata.org/wiki/{entity_id}"
        else:
            return '-'  # Si no hay resultados
    else:
        return '-'

# Ruta de la carpeta donde están los archivos
folder_path = r'C:\Users\adria\TFG\cfkg\BEIS-UK\data'  

# Set para guardar los valores únicos de las columnas 'UOM', 'emission_target_formula', 'GHG' y países
unique_values = set()

# Iterar sobre los archivos CSV en la carpeta
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        
        # Extraer valores únicos de 'UOM', 'emission_target_formula' y 'GHG'
        if 'UOM' in df.columns:
            unique_values.update(df['UOM'].dropna().tolist())
        
        if 'emission_target_formula' in df.columns:
            unique_values.update(df['emission_target_formula'].dropna().tolist())
        
        if 'GHG' in df.columns:
            unique_values.update(df['GHG'].dropna().tolist())
        
        # Extraer países de 'emission_source' cuando empieza con 'Hotel_stay_'
        if 'emission_source' in df.columns:
            for source in df['emission_source'].dropna():
                if source.startswith('Hotel_stay_'):
                    # Extraer el nombre del país quitando el prefijo 'Hotel_stay_'
                    country = source.replace('Hotel_stay_', '').replace('_', ' ')
                    unique_values.add(country)

# Convertir el set de nuevo a lista
unique_values_list = list(unique_values)

# Diccionario para almacenar los datos para el DataFrame
data = {
    'label': [],
    'label_url': []
}

# Iterar sobre cada valor único y buscar en Wikidata
for value in unique_values_list:
    data['label'].append(value)
    data['label_url'].append(search_wikidata(value))

# Crear un DataFrame de pandas con los datos
df = pd.DataFrame(data)

# Guardar el DataFrame en un archivo Excel
output_file = 'unique_values_wikidata_urls2.xlsx'
df.to_excel(output_file, index=False)

print(f"Archivo '{output_file}' creado con éxito.")
