import pandas as pd
import os

def clean_parentheses(text):
    if not isinstance(text, str):  # Check if not a string
        return text  # Return the original value if it's not a string
    if '(' in text:
        return text.split('(')[0].strip()  # Take the part before parentheses and remove spaces
    else:
        return text.strip()  # If no parentheses, return the original text without extra spaces

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

# List to store unique UOM values
unique_uom = set()

# Filter and save information by year
for year in years:
    try:
        df_year = df[df['Year'] == year].copy()  # Create a copy of the filtered DataFrame
        
        # Rename columns
        rename_cols = {
            'Pollutant': 'emission_target',
            'Sector': 'Level 1',
            'Source': 'Level 2',
            'Fuel Name': 'Level 3',
            'NFR Code': 'Column Text',
            'Activity Units': 'UOM',
            'Units': 'GHG'
        }
        df_year.rename(columns=rename_cols, inplace=True)
        
        # Collect unique values from the current year's UOM column
        unique_uom.update(df_year['UOM'].dropna().unique())
        print(df_year.columns)
    except Exception as e:
        print(f"Error processing year {year}: {e}")