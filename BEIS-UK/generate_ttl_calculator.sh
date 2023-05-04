#!/bin/bash

## Remember to first install and activate morph-kgc
echo "Remember install and activate morph-kgc"

python -m morph_kgc cf_ml_calc.ini
echo "Generating TTL file..."
python nt_to_ttl.py out_cf_ml_calc_v2.nt out_cf_ml_calc_v2.ttl
mv out_cf_ml_calc_v2.nt graphs/nt/out_cf_ml_calc_v2.nt
mv out_cf_ml_calc_v2.ttl graphs/ttl/out_cf_ml_calc_v2.ttl

