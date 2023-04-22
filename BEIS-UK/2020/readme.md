Publisher: BEIS (UK)

Mapping conversion for year 2020 (data  has been mapped to Wikidata using OpenRefine)

To run mappings, execute: `python -m morph_kgc cf_2020.ini`

Output will be generated in `nt`, it can be transformed to `ttl` using the script `nt_to_ttl.py`. Usage: `python nt_to_ttl.py source_file.nt target_file.ttl`. The result will be the target ttl file.