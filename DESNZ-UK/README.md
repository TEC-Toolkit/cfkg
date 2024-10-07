## RDF generation process.

Steps needed to create the RDF in TTL:
1. Install [morph-kgc](https://github.com/oeg-upm/morph-kgc) in a new python or conda environment.
2. Install the [yarrrml-parser] (https://github.com/rmlio/yarrrml-parser) which will convert the .yaml files to rml mappings that are needed y morph-kgc
3. Run one of the configuration files (right now this is done one by one). For example: `python -m morph_kgc cf_2023_v2.ini`
4. install `rdflib`. 
5. Morph-kgc will produce an output file in n-triples. These are lengthy, so the script nt_to_ttl transforms them into turtle files. Usage: `python nt_to_ttl.py source_file.nt target_file.ttl`. The result will be the target ttl file.

