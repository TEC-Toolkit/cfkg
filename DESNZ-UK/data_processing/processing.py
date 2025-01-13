```python
import pandas as pd
from datetime import datetime
import os

def get_formula(text):
    formulas = text.split(' per ')[0].strip()  # Takes the part before 'per'
    if len(formulas) > 1:
        if 'kg' in formulas:
            formulas = formulas.replace('kg', '').strip()  # Removes 'kg' if present
        return formulas
    else:
        return formulas[0]  # If not, returns the first

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
        return 'United Kingdom'

def nomenclature(formula):
    if formula is None or pd.isna(formula):  # Checks if the value is None or NaN
        return None
    if 'of' in formula:  # Checks if 'of' is in the formula
        formula1, formula2 = formula.split(' of ')  # Splits the string into two parts
        # Perform mapping using the tuplas_nomen dictionary
        formula1_mapped = tuplas_nomen.get(formula1.strip(), formula1.strip())
        formula2_mapped = tuplas_nomen.get(formula2.strip(), formula2.strip())
        result = f"{formula1_mapped} of {formula2_mapped}"
        return result
    else:
        # Maps directly if the formula does not contain 'of'
        return tuplas_nomen.get(formula.strip(), formula.strip())

def calculate_gwp(row, year_dataset, value):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # Create a dictionary
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["value"]))
    return gwp_dict.get(row["emission_target_formula_aux"], value)

def id_gwp(row, year_dataset, value):
    # Filter by year
    relevant_gwp = df_GWP[(df_GWP['start'] <= year_dataset) & (df_GWP['end'] >= year_dataset)]
    # Create a dictionary
    gwp_dict = dict(zip(relevant_gwp["emission_source"], relevant_gwp["id"]))
    return gwp_dict.get(row["emission_target_formula_aux"], value)

# Path to the Excel file
script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, "../data_raw/ghg-conversion-factors-2023-flat-file-update.xlsx")
df_raw = pd.read_excel(path, sheet_name='Factors by Category', engine='openpyxl')

i = 0
headers = []
while 'Scope' not in headers:
    i += 1
    headers = df_raw.iloc[i].tolist()
df_raw = pd.read_excel(path, sheet_name='Factors by Category', engine='openpyxl', header=i+1)

# Check if there is no 'ID' column and add it if missing
if not any(col.lower() == 'id' for col in headers):
    headers.insert(0, 'id')
df_final = pd.DataFrame(columns=headers)
if 'GHG/Unit' in headers:
    ghg_label = 'GHG/Unit'
else:
    ghg_label = 'GHG'
df_final.pop(ghg_label)

# Populate df_final with data from df_raw
for j in range(len(df_raw)):
    row = df_raw.iloc[j].values.tolist()
    if 'id' in df_final.columns:  # If 'id' was manually added
        row.insert(0, None)  # Insert None at the beginning to align with 'id'
    row = row[:len(headers)]  # Ensure the row has the same length as 'headers'
    df_final.loc[j, headers[:len(row)]] = row
df_final.rename(columns={'ID': 'id'}, inplace=True)
print("Initial lines", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
df_raw[ghg_label] = df_raw[ghg_label].astype(str)
column_name = [col for col in df_raw.columns if 'GHG Conversion Factor' in col][0]
year_dataset = int(column_name.split()[-1])

df_final['Scope'] = df_final['Scope'].astype(str).str.replace(' ', '', regex=False)
df_final.insert(7, "emission_source", None)
df_final['emission_source'] = df_final['Level 2'].astype(str).str.replace(" ", "_", regex=False) + "_" + df_final['Level 3'].astype(str).str.replace(" ", "_", regex=False)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Load the Excel file with labels and URLs
path_labels = os.path.join(script_dir, "../../auxiliary_op/unique_values_wikidata_urls.xlsx")
df_labels = pd.read_excel(path_labels, engine='openpyxl')

# Create a dictionary of labels and their URLs
tuplas = dict(zip(df_labels['label'], df_labels['label_url']))
# Extract URL values for columns in df_final ending with '_wd'
for col in df_final.columns:
    if col.endswith('_wd'):
        # Get the base column without '_wd' and replace it with URLs from the dictionary
        base_col = col[:-3]
        df_final[col] = df_final[base_col].map(tuplas).fillna('-')

# ---------------------- Other transformations ----------------------
df_final['UOM'] = df_final['UOM'].fillna('').astype(str)
df_final['UOM'] = df_final['UOM'].apply(clean_parentheses)
print("Lines 1", df_final.shape[0])

# Create 'UOM_wd' column by mapping values of 'UOM' to the dictionary of labels and URLs (tuplas)
df_final['UOM_wd'] = df_final['UOM'].map(tuplas)
# Reorder columns so 'UOM_wd' appears right after 'UOM'
columns = list(df_final.columns)
index_uom = columns.index('UOM')
columns.insert(index_uom + 1, columns.pop(columns.index('UOM_wd')))
df_final = df_final[columns]
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extract and clean 'emission_target_formula'
df_final['emission_target_formula'] = df_raw[ghg_label].apply(get_formula)
df_final['emission_target_formula'] = df_final['emission_target_formula'].apply(lambda x: x.replace('kg', '').strip() if isinstance(x, str) else x)
df_final['emission_target_formula'] = df_final['emission_target_formula'].replace('nan', None)
# Clean parentheses values in both columns
df_final['emission_target_formula'] = df_final['emission_target_formula'].str.replace("(Net CV)", "", regex=False).str.replace("(Gross CV)", "", regex=False).str.replace("(net)", "", regex=False).str.replace("kWh ", "kWh", regex=False)
df_final[ghg_label] = df_raw[ghg_label].str.replace("(Net CV)", "", regex=False).str.replace("(Gross CV)", "", regex=False).str.replace("(net)", "", regex=False)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Load the Excel file with formulas and their corresponding nomenclatures
path_nomen = os.path.join(script_dir, "../../auxiliary_op/formulas.xlsx")
df_nomen = pd.read_excel(path_nomen, engine='openpyxl')

df_final['emission_target_formula_aux'] = df_final['emission_target_formula'].str.split().str[-1]
# Create a dictionary of formulas and nomenclatures
tuplas_nomen = dict(zip(df_nomen['formula'], df_nomen['nomenclature']))
df_final['emission_target'] = df_final['emission_target_formula'].apply(nomenclature)
df_final = df_final.dropna(subset=['emission_target_formula'])

df_final['emission_target_wd'] = df_final['emission_target_formula'].map(tuplas)
print("Lines 2", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extract 'GHG' from the 'GHG/Unit' field
df_final['GHG/Unit'] = df_final['GHG/Unit'].str.replace(' per unit', '', regex=False)
df_final['GHG'] = df_raw[ghg_label].str.split().str[0]
df_final['GHG'] = df_final['GHG'].replace('nan', None)
# Identify rows where df_final['GHG'] is equal to 'kWh'
rows_to_delete = df_final[df_final['GHG'] == 'kWh'].index
# Remove those rows
df_final = df_final.drop(rows_to_delete)
df_final['GHG_wd'] = df_final['GHG'].map(tuplas)
print("Lines 4", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Set date validity columns
df_final['valid_from'] = datetime(year_dataset, 1, 1, 0, 0, 0).isoformat()
df_final['valid_to'] = datetime(year_dataset, 12, 31, 23, 59, 59).isoformat()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Apply the function to the 'region' column
df_final['region'] = df_final['emission_source'].apply(get_region)
df_final['region_wd'] = df_final['region'].map(tuplas)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
df_final = df_final.rename(columns={f'GHG Conversion Factor {year_dataset}': f'Conversion Factor {year_dataset}'})
# Ensure values are of string type to use .str.replace() and convert to numeric
df_final[f'Conversion Factor {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}'].astype(str)
df_final[f'Conversion Factor {year_dataset}'] = pd.to_numeric(df_final[f'Conversion Factor {year_dataset}'].str.replace(',', '', regex=False), errors='coerce')
print("Lines 5", df_final.shape[0])

# Drop rows with NaN in 'Conversion Factor {year_dataset}'
df_final = df_final.dropna(subset=[f'Conversion Factor {year_dataset}'])
print("Lines 6", df_final.shape[0])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GWP
path_GWP_values = os.path.join(script_dir, "../../GWP/GWP_values.xlsx")
df_GWP = pd.read_excel(path_GWP_values, engine='openpyxl')

df_final['GWP'] = df_final.apply(lambda row: calculate_gwp(row, year_dataset, 1), axis=1)
df_final[f'Value {year_dataset}'] = df_final[f'Conversion Factor {year_dataset}'] / df_final['GWP']
df_final['GWP'] = df_final.apply(lambda row: calculate_gwp(row, year_dataset, ''), axis=1)
df_final['GWP_id'] = df_final.apply(lambda row: id_gwp(row, year_dataset, ''), axis=1)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Move 'Conversion Factor {year_dataset}' to the last position
conversion_factor_column = f'Conversion Factor {year_dataset}'
columns = [col for col in df_final.columns if col != conversion_factor_column] + [conversion_factor_column]
df_final = df_final[columns]
# Rename columns and ensure they are stripped of whitespace
df_final.columns = df_final.columns.str.strip()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# If 'id' was manually added in 'headers', generate ID values
if 'id' in df_final.columns and df_final['id'].isnull().all():
    df_final['id'] = range(1, len(df_final) + 1)

# Remove 'emission_target_formula_aux' column
df_final = df_final.drop(columns=['emission_target_formula_aux'])
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Save to Excel
final_path = os.path.join(script_dir, f"../data/v3/Conversion_Factor_{year_dataset}.csv")
df_final.to_csv(final_path, index=False)
print("Final lines", df_final.shape[0])
```