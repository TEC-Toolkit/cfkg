import re

file_path = "out_cf_2019_v3.nt"

with open(file_path, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        # Patrón que busca líneas de tripletas correctas
        if not re.match(r'^<[^>]+>\s+<[^>]+>\s+.+\.$', line.strip()):
            print(f"Línea {line_number}: {line.strip()}")
