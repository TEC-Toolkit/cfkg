# Conversion factor Knowledge Graph
[![DOI](https://zenodo.org/badge/566371476.svg)](https://zenodo.org/badge/latestdoi/566371476)

This repository contains the data cleaning steps and mappings of the conversion factor knowledge graph. At the moment, public data includes:

- BEIS-UK, from years 2016-2022
    - Data is licensed under an [Open Governemnt license](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
    - Each data source used is linked in each conversion factor in the KG

- Machine Learning impact calculator, from years 2002-2018
    - Data is licensed under a [MIT license](https://github.com/mlco2/impact/blob/master/LICENSE)
    - Each data source used is linked in each conversion factor in the KG

Work in progress:
- EPA

## Query interface
A derreferenceable linked data browser is available at: [https://query.cf.linkeddata.es/query](https://query.cf.linkeddata.es/query), based on https://github.com/TEC-Toolkit/rdf_explorer.

To see information about a conversion factor, just click on its URL, e.g., [https://w3id.org/ecfkg/i/UK/BEIS/2021/CF_1](https://w3id.org/ecfkg/i/UK/BEIS/2021/CF_1). 


## SPARQL endpoint

All data is loaded in [https://sparql.cf.linkeddata.es/cf](https://sparql.cf.linkeddata.es/cf), in the `cf` dataset. To perform a query, just URL encode the query:
```
curl https://sparql.cf.linkeddata.es/cf -X POST --data 'query=YOUR_QUERY_URL_ENCODED' -H 'Accept: application/sparql-results+json,*/*;q=0.9'
```

For example, the following query retrieves the conversion factors that involve "Butane" (and their corresponding basic metadata)

Sparql: 
```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ecfo: <https://w3id.org/ecfo#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select  ?cf ?source ?context ?target ?scope where{
    ?cf ecfo:hasTag/rdfs:label "Butane"@en.
    ?cf ecfo:hasEmissionTarget/rdfs:label ?target.
    ?cf ecfo:hasEmissionSource/rdfs:label ?source.
    ?cf ecfo:hasAdditionalContext ?context.
    ?cf ecfo:hasScope ?scope.
}
```
Corresponding curl command:
```
curl https://sparql.cf.linkeddata.es/cf -X POST --data 'query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX+ecfo%3A+%3Chttps%3A%2F%2Fw3id.org%2Fecfo%23%3E%0APREFIX+time%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2006%2Ftime%23%3E%0APREFIX+dc%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Felements%2F1.1%2F%3E%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0A%0Aselect++%3Fcf+%3Fsource+%3Fcontext+%3Ftarget+%3Fscope+where%7B%0A++++%3Fcf+ecfo%3AhasTag%2Frdfs%3Alabel+%22Butane%22%40en.%0A++++%3Fcf+ecfo%3AhasEmissionTarget%2Frdfs%3Alabel+%3Ftarget.%0A++++%3Fcf+ecfo%3AhasEmissionSource%2Frdfs%3Alabel+%3Fsource.%0A++++%3Fcf+ecfo%3AhasAdditionalContext+%3Fcontext.%0A++++%3Fcf+ecfo%3AhasScope+%3Fscope.%0A%7D' -H 'Accept: application/sparql-results+json,*/*;q=0.9'
```

## Tutorial
Have a look at [our tutorial](tutorial/Using_CFKG_Evolution_of_Conversion_Factors_through_the_years.ipynb), showing how to plot the evolution of a conversion factor through the years, together with the corresponding SPARQL queries needed to adapt it to your own.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the process for submitting pull requests to this repository. 
