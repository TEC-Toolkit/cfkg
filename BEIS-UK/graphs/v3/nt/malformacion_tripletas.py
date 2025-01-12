import pandas as pd

def detectar_valores_vacios(ruta_csv):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(ruta_csv)
        
        # Buscar filas que contengan valores vacíos
        filas_vacias = df[df.isnull().any(axis=1)]

        if filas_vacias.empty:
            print("No se encontraron valores vacíos en el CSV.")
        else:
            print(f"Se encontraron {len(filas_vacias)} filas con valores vacíos:")
            for index, row in filas_vacias.iterrows():
                columnas_vacias = row[row.isnull()].index.tolist()
                print(f"Línea {index + 2}: columnas vacías -> {columnas_vacias}")  # +2 para contar encabezado y línea base

    except Exception as e:
        print(f"Error al leer el archivo: {e}")

# Ruta al archivo CSV
ruta_csv = r"C:\Users\adria\TFG\cfkg\BEIS-UK\data\v3\Conversion_Factor_2019_v3.csv"

detectar_valores_vacios(ruta_csv)
