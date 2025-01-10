import re

def remove_malformed_lines(input_file, output_file):
    # Regex pattern for a valid N-Triples line: <sujeto> <predicado> <objeto> .
    nt_pattern = re.compile(r'^<[^>]+> <[^>]+> <[^>]+> \.$')
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Keep only the lines that match the valid pattern
    valid_lines = [line for line in lines if nt_pattern.match(line.strip())]

    # Write the valid lines to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(valid_lines)

    print(f"Malformed lines removed. Output saved to {output_file}")

# Example usage
input_file = r'C:\Users\adria\TFG\cfkg\BEIS-UK\out_cf_2022_v2.nt'
output_file = 'good_out_cf_2022_v2.nt'
remove_malformed_lines(input_file, output_file)
