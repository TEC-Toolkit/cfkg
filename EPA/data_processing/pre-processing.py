import re
import pandas as pd
import warnings
import os
import numpy as np

# Function to remove text inside parentheses
def clean_parentheses(text):
    if '(' in text:
        return text.split('(')[0].strip()
    else:
        return text.strip()

# Ignore specific warnings
warnings.filterwarnings("ignore")

# Path to the Excel file
script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, "../data_raw/ghg-emission-factors-hub-2024.xlsx")
df_raw = pd.read_excel(path, sheet_name='Emission Factors Hub', engine='openpyxl')

# ---------------------------------------------------------------------------------------------------------------------------------
# TABLE 1 (Scope 1)
df = df_raw.iloc[15:90, 2:]  # Extract Table 1
df.columns = df_raw.iloc[14, 2:]  # Set header
df = df.reset_index(drop=True)

# Initialize `ghg_units` with the units GHG/Unit
ghg_units = df_raw.iloc[15, 2:].tolist()

# Create empty final DataFrame
df_final = pd.DataFrame(columns=['id', 'Scope', 'Level 1', 'Level 2', 'Level 3', 'Level 4',
                                 'Column Text', 'UOM', 'GHG/Unit', 'Conversion Factor 2024'])

# Temporary variable to store the current category for Level 2
current_level_2 = None

# Process rows of Table 1
for index, row in df.iterrows():
    if pd.isna(row.iloc[0]):  # If the row starts empty
        ghg_units = row.iloc[1:].tolist()  # Update `ghg_units`
    elif pd.notna(row.iloc[0]) and row.iloc[1:].isna().all():
        current_level_2 = row.iloc[0]  # Update Level 2 category
    else:
        # Create rows for each value in `GHG/Unit`
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

# Assign unique IDs
df_final['id'] = range(1, len(df_final) + 1)
print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLE 3 (Scope 1)
df3 = df_raw.iloc[123:235, 2:]  # Extract Table 3
df3.columns = df_raw.iloc[122, 2:]
df3 = df3.loc[:, ~df3.columns.isna()]  # Remove empty columns

current_level_1 = None
current_level_2 = 'On-Road Gasoline Vehicles'
column_text = None
last_id = df_final['id'].max()  # Get last used ID

# Process rows of Table 3 and add directly to df_final
for index, row in df3.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        try:
            column_text, current_level_1 = row['Vehicle Type'].split(' ', 1)
        except ValueError:
            column_text = row['Vehicle Type']
            current_level_1 = ""

    level_3 = row.get('Model Year')
    
    # Create rows for each GHG/Unit
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

print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLE 4 (Scope 1)
df4 = df_raw.iloc[241:275, 2:]  # Extract Table 4
df4.columns = df_raw.iloc[240, 2:]
df4 = df4.loc[:, ~df4.columns.isna()]  # Remove empty columns

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

print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLE 5 (Scope 1)
df5 = df_raw.iloc[282:322, 2:]  # Extract Table 5
df5.columns = df_raw.iloc[281, 2:]
df5 = df5.loc[:, ~df5.columns.isna()]  # Remove empty columns

level_1 = None
level_2 = 'Non-Road Vehicles'
column_text = None

for index, row in df5.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
    if pd.notna(row.get('Fuel Type')):
        column_text = row.get('Fuel Type')
    
    for ghg_unit, conversion_factor in zip(df5.columns[-2:], row[-2:]):
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        new_row = {
            'id': df_final['id'].max() + 1,
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

print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# TABLE 6 (Scope 2)
df6 = df_raw.iloc[330:359, 1:7]
columns_primary = df_raw.iloc[329, 1:7]
columns_secondary = df_raw.iloc[330, 1:7]
df6 = df6.loc[:, ~df6.columns.isna()]
df6.columns = pd.MultiIndex.from_tuples(zip(columns_primary, columns_secondary))

level_2 = None
level_3 = None
for index, row in df6.iterrows():
    if pd.notna(row.get(('eGRID Subregion Name', np.nan))):
        level_3 = row[('eGRID Subregion Name', np.nan)]
    secondary_headers = df6.columns.get_level_values(1)
    
    for ghg_unit, conversion_factor in zip(secondary_headers[~pd.isna(secondary_headers)][-3:], row[-3:]):
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
        new_row = {
            'id': df_final['id'].max() + 1,
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
# TABLE 8 (Scope 3)
df8 = df_raw.iloc[411:418, 2:]
df8.columns = df_raw.iloc[410, 2:]
df8 = df8.loc[:, ~df8.columns.isna()]

level_1 = None
level_2 = 'Downstream Transportation and Distribution'

for index, row in df8.iterrows():
    if pd.notna(row.get('Vehicle Type')):
        level_1 = row.get('Vehicle Type')
    
    for ghg_unit, conversion_factor in zip(df8.columns[-4:], row[1:4]):
        unit = row[df8.columns[-1]]
        ghg_unit = re.search(r'\((.*?)\)', ghg_unit).group(1)
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

print(df_final['id'].max())
# ---------------------------------------------------------------------------------------------------------------------------------
# EXPORT
df_final = df_final.sort_values(by='id').reset_index(drop=True)
final_path = os.path.join(script_dir, f"../data_raw/EPA_raw.xlsx")
df_final.to_excel(final_path, index=False)
