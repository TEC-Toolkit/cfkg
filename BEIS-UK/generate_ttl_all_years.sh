#!/bin/bash

## Remember to first install and activate morph-kgc
echo "Remember to install and activate morph-kgc"

for file in cf_*_v2.ini; do
    if [ -f "$file" ]; then
        echo Dealing with "$file"
	python -m morph_kgc $file
	year=${file:3:4}
	out_nt="out_cf_"$year"_v2.nt"
	out_ttl="out_cf_"$year"_v2.ttl"
	#echo python nt_to_ttl.py $out_nt $out_ttl
	echo "Generating TTL file..."
	python nt_to_ttl.py $out_nt $out_ttl
	mv $out_nt graphs/nt/"$out_nt"
	mv $out_ttl graphs/ttl/"$out_ttl"
	echo "Done!"
    fi
done
