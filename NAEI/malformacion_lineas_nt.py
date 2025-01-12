import re
import os

def remove_malformed_lines(input_file):
    # Regex pattern for a valid N-Triples line: <sujeto> <predicado> <objeto> .
    nt_pattern = re.compile(r'^<[^>]+> <[^>]+> <[^>]+> \.$')
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Keep only the lines that match the valid pattern
    valid_lines = [line for line in lines if nt_pattern.match(line.strip())]

    # Overwrite the same file with valid lines only
    with open(input_file, 'w', encoding='utf-8') as file:
        file.writelines(valid_lines)

    print(f"Malformed lines removed. File overwritten: {input_file}")

def process_all_nt_files(folder):
    # Iterate over all .nt files in the folder
    for filename in os.listdir(folder):
        if filename.endswith('.nt'):
            input_file = os.path.join(folder, filename)
            remove_malformed_lines(input_file)

# Example usage
script_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(script_dir, f"graphs/v3/nt")
process_all_nt_files(folder)
