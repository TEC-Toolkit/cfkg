```python
import pandas as pd
from datetime import datetime
import os

# Custom function to get the second formula if it exists, otherwise return the first
def get_formula(text):
    if len(text) > 1:
        if text.split()[0] in ['kg', 'g', 'lb']:
            return text.split()[1]
        else:
            return text.split()[0]
    else:
        return text  # If not, return the first

# Function to remove net/gross CV to add the Wikidata URL later
def clean_parentheses(text):
    if '(' in text:
        return text.split('(')[0].strip()  # Takes the part before the parentheses and removes spaces
    else:
        return text.strip()  # If there are no parentheses, returns the original text without additional spaces

# Modify the 'region' column based on 'emission_source'
def get_region(emission_source):
    if emission_source.startswith('Hotel_stay'):
        # Remove the 'Hotel_stay_' prefix and replace '_' with spaces
        return emission_source.replace('Hotel_stay_', '').replace('_', ' ')
    else:
        return 'United States'

def calculate_gwp(row, year_dataset, value):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["value"]))
    return gwp_dict.get(row["emission_target_formula_aux"], value)

def id_gwp(row, year_dataset, value):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["id"]))
    return gwp_dict.get(row["emission_target_formula_aux"], value)
        
def conversion_units(unit, conversion_value):
    # Adjust values of 'Conversion Factor 2024' and change 'GHG' from 'g' to 'kg'
    mask = df_final['GHG'] == unit
    df_final.loc[mask, 'Conversion Factor 2024'] /= conversion_value
    df_final.loc[mask, 'GHG'] = 'kg'

    mask_ghg_unit = df_final['GHG/Unit'].str.startswith(f'{unit} ', na=False)
    df_final.loc[mask_ghg_unit, 'GHG/Unit'] = df_final['GHG/Unit'].str.replace(f'^{unit} ', 'kg ', regex=True)

# Path to the Excel file
script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, "../data_raw/EPA_raw.xlsx")
df_raw = pd.read_excel(path, sheet_name='Sheet1', engine='openpyxl')

# GWP
path_GWP_values = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
df_GWP = pd.read_excel(path_GWP_values, engine='openpyxl')

# Load the Excel file with labels and URLs
path_labels = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
df_labels = pd.read_excel(path_labels, engine='openpyxl')

headers = df_raw.columns
df_final = pd.DataFrame(columns=headers)
ghg_label = 'GHG/Unit' if 'GHG/Unit' in headers else 'GHG'
df_final.pop(ghg_label)

# Populate df_final with data from df_raw
for j in range(len(df_raw)):
    row = df_raw.iloc[j].values.tolist()
    row = row[:len(headers)]
    df_final.loc[j, headers[:len(row)]] = row

print("Initial lines", df_final.shape[0])

df_raw[ghg_label] = df_raw[ghg_label].astype(str)
year_dataset = 2024

df_final['Scope'] = df_final['Scope'].astype(str).str.replace(' ', '', regex=False)
df_final.insert(7, "emission_source", None)
df_final['emission_source'] = df_final['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" + df_final['Level 3'].astype(str).str.replace(" ", "_", regex=False)

# Create a dictionary of labels and their URLs
tuplas = dict(zip(df_labels['label'], df_labels['label_url']))

# Map URL values for columns ending with '_wd'
for col in df_final.columns:
    if col.endswith('_wd'):
        base_col = col[:-3]
        df_final[col] = df_final[base_col].map(tuplas).fillna('-')

# ---------------------- Other transformations ----------------------
df_final['UOM'] = df_final['UOM'].fillna('').astype(str)
df_final['UOM'] = df_final['UOM'].apply(clean_parentheses)
print("Lines 1", df_final.shape[0])

# Create 'UOM_wd' column by mapping UOM values to URLs
df_final['UOM_wd'] = df_final['UOM'].map(tuplas)
columns = list(df_final.columns)
index_uom = columns.index('UOM')
columns.insert(index_uom + 1, columns.pop(columns.index('UOM_wd')))
df_final = df_final[columns]

# Extract and clean 'emission_target_formula'
df_final['emission_target_formula'] = df_raw[ghg_label].apply(get_formula)
df_final['emission_target_formula'] = df_final['emission_target_formula'].replace('nan', None)
df_final['emission_target_formula'] = df_final['emission_target_formula'].str.replace('mmBtu', '', regex=False)
df_final[ghg_label] = df_raw[ghg_label]
print("Lines 2", df_final.shape[0])

# Load the Excel file with formulas and nomenclatures
path_nomen = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
df_nomen = pd.read_excel(path_nomen, engine='openpyxl')

df_final['emission_target_formula_aux'] = df_final['emission_target_formula'].str.split().str[-1]
tuplas_nomen = dict(zip(df_nomen['formula'], df_nomen['nomenclature']))
df_final['emission_target'] = df_final['emission_target_formula_aux'].map(tuplas_nomen)
df_final = df_final.dropna(subset=['emission_target_formula'])

df_final['emission_target_wd'] = df_final['emission_target_formula_aux'].map(tuplas)
print("Lines 3", df_final.shape[0])

# Extract 'GHG' from the 'GHG/Unit' field
df_final['GHG/Unit'] = df_final['GHG/Unit'].str.replace(' per unit', '', regex=False)
df_final = df_final[~df_final['GHG/Unit'].str.contains('mmBtu', na=False)]

df_final['GHG'] = df_raw[ghg_label].str.split().str[0]
df_final['GHG'] = df_final['GHG'].replace('nan', None)

# Convert units
conversion_units('g', 1000)
conversion_units('lb', 2.20462)

# Remove rows where GHG equals 'kWh'
rows_to_delete = df_final[df_final['GHG'] == 'kWh'].index
df_final = df_final.drop(rows_to_delete)

df_final['GHG_wd'] = df_final['GHG'].map(tuplas)
df_final['valid_from'] = datetime(year_dataset, 1, 1, 0, 0, 0).isoformat()
df_final['valid_to'] = datetime(year_dataset, 12, 31, 23, 59, 59).isoformat()
print("Lines 4", df_final.shape[0])

# Apply the function to the 'region' column
df_final['region'] = df_final['emission_source'].apply(get_region)
df_final['region_wd'] = df_final['region'].map(tuplas)

df_final[f'Conversion Factor {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}'].astype(str)
df_final[f'Conversion Factor {year_dataset}'] = pd.to_numeric(df_final[f'Conversion Factor {year_dataset}'].str.replace(',', '', regex=False), errors='coerce')
print("Lines 5", df_final.shape[0])

# Remove rows with NaN in 'Conversion Factor {year_dataset}'
df_final = df_final.dropna(subset=[f'Conversion Factor {year_dataset}'])
print("Lines 6", df_final.shape[0])

# Move 'Conversion Factor {year_dataset}' to the last position
conversion_factor_column = f'Conversion Factor {year_dataset}'
columns = [col for col in df_final.columns if col != conversion_factor_column] + [conversion_factor_column]
df_final = df_final[columns]

# Rename and clean column names
df_final.columns = df_final.columns.str.strip()

df_final['GWP'] = df_final.apply(lambda row: calculate_gwp(row, year_dataset, 1), axis=1)
df_final[f'Value {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}'] * df_final['GWP']
df_final['GWP'] = df_final.apply(lambda row: calculate_gwp(row, year_dataset, ''), axis=1)
df_final['GWP_id'] = df_final.apply(lambda row: id_gwp(row, year_dataset, ''), axis=1)

# Add CO2e rows to DataFrame
groups = df_final.groupby('emission_source')
new_rows = []

for emission_source, group in groups:
    sum_conversion = group['Conversion Factor 2024'].sum()
    last_row = group.iloc[-1].copy()
    new_row = last_row.copy()
    if pd.notna(last_row['GHG/Unit']):
        words = str(last_row['GHG/Unit']).split(' ')
        if len(words) > 1:
            words[1] = 'CO2e'
            new_row['GHG/Unit'] = ' '.join(words)
    else:
        new_row['GHG/Unit'] = 'kg CO2e'

    new_row['Conversion Factor 2024'] = sum_conversion
    new_row['emission_target_formula'] = 'CO2e'
    new_row['emission_target'] = tuplas_nomen.get('CO2e', None)
    new_row['emission_target_wd'] = tuplas.get('CO2e', None)
    new_row['GWP'] = None
    new_row['GWP_id'] = None
    new_row[f'Value {year_dataset}'] = new_row['Conversion Factor 2024']
    new_rows.append((group.index[-1], new_row))

for index, row in sorted(new_rows, reverse=True):
    df_final = pd.concat([df_final.iloc[:index + 1], pd.DataFrame([row]), df_final.iloc[index + 1:]]).reset_index(drop=True)

df_final = df_final.drop(columns=['emission_target_formula_aux'])

# Generate ID if 'id' column exists
if 'id' in df_final.columns:
    df_final['id'] = range(1, len(df_final) + 1)

# Save to Excel
final_path = os.path.join(script_dir, f"../data/Conversion_Factor_{year_dataset}.xlsx")
df_final.to_excel(final_path, index=False)
print("Final lines", df_final.shape[0])
```