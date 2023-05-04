# Conversion factor Knowledge Graph
This repository contains the data cleaning steps and mappings of the conversion factor knowledge graph. At the moment, public data includes:

- BEIS-UK, from years 2016-2022

Work in progress:
- EPA


All data is loaded in [https://sparql.cf.linkeddata.es/](https://sparql.cf.linkeddata.es/), in the `cf` dataset. To perform a query, just URL encode it:
```
curl https://sparql.cf.linkeddata.es/cf -X POST --data 'query=YOUR_QUERY_URL_ENCODED' -H 'Accept: application/sparql-results+json,*/*;q=0.9'
```
