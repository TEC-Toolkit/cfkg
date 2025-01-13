from datetime import datetime
import re
import pandas as pd
import os

def clean_parentheses(text):
    if not isinstance(text, str):  # Check if not a string
        return text  # Return the original value if it's not a string
    if '(' in text:
        return text.split('(')[0].strip()  # Take the part before parentheses and remove spaces
    else:
        return text.strip()  # If no parentheses, return the original text without extra spaces

def calculate_gwp(row, year_dataset):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["value"]))
    return gwp_dict.get(row["emission_target_formula"])

def id_gwp(row, year_dataset):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["id"]))
    return gwp_dict.get(row["emission_target_formula"])

# Function to extract the part after the underscore if it starts with a number
def modify_column_text(text):
    if pd.notna(text) and re.match(r'^\d', text):  # Check if not NaN and starts with a number
        parts = text.split('_', 1)
        return parts[1] if len(parts) > 1 else text  # Return the part after '_' if it exists
    return text  # Return the original text if it doesn't match the condition

def kilotonne_to_kg(df, year_dataset):
    # Mask to identify rows where 'GHG' is 'kilotonne'
    mask = df['GHG'] == 'kilotonne'
    # Replace 'kilotonne' with 'kg' in the 'GHG' column
    df.loc[mask, 'GHG'] = 'kg'
    conversion_column = f'Conversion Factor {year_dataset}'
    df.loc[mask, conversion_column] = df.loc[mask, conversion_column] * 1e6

def define_scope(row):
    """
    Function to define the scope based on 'Level 1' value.

    - If 'Level 1' is "Agriculture" or "Industrial Processes and Other Product Use" -> scope1.
    - If 'Level 1' is "Energy" -> scope2.
    - Any other value -> scope3.
    """
    if row['Level 1'] in ['Agriculture', 'Industrial Processes and Other Product Use']:
        return 'Scope1'
    elif row['Level 1'] == 'Energy':
        return 'Scope2'
    else:
        return 'Scope3'

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, "../data_raw/export.xlsx")

# Read the Excel file
try:
    df = pd.read_excel(path, sheet_name='export', engine='openpyxl')
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    exit()

# Check if the 'Year' column exists
if 'Year' not in df.columns:
    print(f"Error: The 'Year' column does not exist in the Excel file.")
    exit()

# Get unique years
years = df['Year'].unique()

# Filter and save information by year
for year in years:
    try:
        df_year = df[df['Year'] == year].copy()  # Create a copy of the filtered DataFrame
        #-------------------------------------------------------------------------------------------
        # Rename columns
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
        df_year.rename(columns=rename_cols, inplace=True)
        #-------------------------------------------------------------------------------------------
        # Apply the function to the 'Column Text' column
        df_year['Column Text'] = df_year['Column Text'].apply(modify_column_text)
        #-------------------------------------------------------------------------------------------
        # Load formulas and map them
        nomenclature_path = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
        df_nomen = pd.read_excel(nomenclature_path, engine='openpyxl')
        tuplas_nomen = dict(zip(df_nomen['nomenclatura'], df_nomen['formula']))

        df_year['emission_target_formula'] = df_year['emission_target'].map(tuplas_nomen)
        #-------------------------------------------------------------------------------------------
        # Create new columns
        df_year['emission_source'] = (
            df_year['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" +
            df_year['Level 3'].astype(str).str.replace(" ", "_", regex=False)
        )
        #-------------------------------------------------------------------------------------------
        # Remove rows where 'UOM' is empty
        df_year = df_year[df_year['UOM'].str.strip() != '']
        df_year = df_year.dropna(subset=['UOM'])
        #-------------------------------------------------------------------------------------------
        # Apply conversion function
        kilotonne_to_kg(df_year, year)
        df_year['GHG/Unit'] = df_year['GHG'].astype(str) + " " + df_year['emission_target_formula']
        #-------------------------------------------------------------------------------------------
        # Load labels and URLs
        labels_path = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
        df_labels = pd.read_excel(labels_path, engine='openpyxl')
        tuplas = dict(zip(df_labels['label'], df_labels['label_url']))
        df_year['UOM_wd'] = df_year['UOM'].apply(clean_parentheses).map(tuplas)
        df_year['GHG_wd'] = df_year['GHG'].map(tuplas)
        df_year['emission_target_wd'] = df_year['emission_target_formula'].map(tuplas)
        #-------------------------------------------------------------------------------------------
        df_year['region'] = 'United Kingdom'
        df_year['region_wd'] = df_year['region'].map(tuplas)
        #-------------------------------------------------------------------------------------------
        # Add dates and additional columns
        df_year['valid_from'] = datetime(year, 1, 1, 0, 0, 0).isoformat()
        df_year['valid_to'] = datetime(year, 12, 31, 23, 59, 59).isoformat()
        #-------------------------------------------------------------------------------------------
        # Apply the function to define scope
        df_year['Scope'] = df_year.apply(define_scope, axis=1)
        df_year['Level 4'] = None
        df_year = df_year[df_year['emission_target'] != 'Bio-Carbon']

        # GWP
        gwp_path = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
        df_GWP = pd.read_excel(gwp_path, engine='openpyxl')

        df_year['GWP'] = df_year.apply(lambda row: calculate_gwp(row, year), axis=1)
        df_year[f'Value {year}'] = df_year[f'Conversion Factor {year}'] / df_year['GWP']
        df_year['GWP_id'] = df_year.apply(lambda row: id_gwp(row, year), axis=1)
        #-------------------------------------------------------------------------------------------
        # Generate unique IDs
        df_year['id'] = range(1, len(df_year) + 1)
        #-------------------------------------------------------------------------------------------
        # Reorder columns
        new_order = [
            'id', 'Scope', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Column Text',
            'emission_source', 'UOM', 'UOM_wd', 'GHG/Unit', 'emission_target_formula',
            'emission_target', 'emission_target_wd', 'GHG', 'GHG_wd',
            'valid_from', 'valid_to', 'region', 'region_wd', f'Conversion Factor {year}', 
            f'Value {year}', 'GWP', 'GWP_id'
        ]
        df_year = df_year[new_order]
        #-------------------------------------------------------------------------------------------
        # Save the Excel file
        output_file = os.path.join(script_dir, f"../data/v3/Conversion_Factor_{year}.csv")
        df_year.to_csv(output_file, index=False)
        print(f"File saved: Conversion_Factor_{year}.csv")
    except Exception as e:
        print(f"Error processing year {year}: {e}")
