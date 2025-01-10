import pandas as pd
import requests
from rdflib import Graph, URIRef, Literal, Namespace

def limpiar_parentesis(text):
    if isinstance(text, str):  # Solo procede si es una cadena
        return text.split('(')[0].strip()  # Elimina el contenido entre paréntesis
    return text

def obtener_formula(text):
    # Verificar si el valor es una cadena
    if isinstance(text, str):
        formulas = text.split(' of ')  # Separa las fórmulas usando ' of ' como delimitador
        if len(formulas) > 1:
            second_formula = formulas[1].split(' per ')[0].strip()  # Toma lo que esté antes de 'per'
            return second_formula
        else:
            return formulas[0]  # Si no, devuelve la primera
    # Si no es una cadena (por ejemplo, NaN), devuelve None o un valor predeterminado
    return None

def wikidata_url(objetivo: str): 
    # Definir el endpoint de la API de Wikidata
    url = "https://www.wikidata.org/w/api.php"

    # Parámetros para hacer una búsqueda en Wikidata
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'search': objetivo
    }

    # Hacer la solicitud HTTP a la API de Wikidata
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanzar un error si la solicitud no tiene éxito
        data = response.json()

        # Verificar si el campo 'search' existe en la respuesta
        if 'search' in data and len(data['search']) > 0:
            entity_id = data['search'][0]['id']  # Obtener el ID de la entidad
            entity_url = f"https://www.wikidata.org/wiki/{entity_id}"  # Construir la URL de Wikidata
            return entity_url
        else:
            return "Error"

    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud para '{objetivo}': {e}")
        return "Error"
#------------------------------------------------------------------------------------------
ruta = r"C:\Users\adria\TFG\cfkg\DESNZ-UK\data_raw\ghg-conversion-factors-2023-flat-file-update.xlsx"
df = pd.read_excel(ruta, sheet_name='Factors by Category', engine='openpyxl')
# Cargar el archivo Excel
i=0
cabeceras = []
while 'Scope' not in cabeceras:
    i+=1
    cabeceras = df.iloc[i].tolist()
df = pd.read_excel(ruta, sheet_name='Factors by Category', engine='openpyxl', header = i+1)
datos_extraer = []
df['UOM'] = df['UOM'].apply(limpiar_parentesis)
df.loc[:, 'emission_target_formula'] = df['GHG/Unit'].apply(obtener_formula)
df['emission_target_formula'] = df['emission_target_formula'].apply(lambda x: x.replace('kg', '').strip() if isinstance(x, str) else x)
df['emission_target_formula'] = df['emission_target_formula'].apply(limpiar_parentesis)
datos_extraer.extend(df['UOM'].unique().tolist())
datos_extraer = [x for x in datos_extraer if pd.notna(x)]

datos_extraer.extend(df['emission_target_formula'].unique().tolist())
datos_extraer = [x for x in datos_extraer if x is not None]

print(datos_extraer)
g = Graph()
g.bind("fn", "http://www.w3.org/2005/xpath-functions#")
g.bind("owl", "http://www.w3.org/2002/07/owl#")
g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
g.bind("schema", "https://schema.org/")
g.bind("qudt", "http://qudt.org/schema/qudt/")
ns = Namespace("http://example.org/")

for dato in datos_extraer:
    url = wikidata_url(dato)
    g.add((URIRef(url), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(dato)))

g.serialize("wikidata_labels.ttl", format="turtle")