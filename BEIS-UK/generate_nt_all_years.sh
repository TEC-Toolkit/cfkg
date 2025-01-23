#!/bin/bash

## Remember to first install and activate morph-kgc
echo "Remember to install and activate morph-kgc"

for file in cf_*_v3.ini; do
    if [ -f "$file" ]; then
        echo Dealing with "$file"
	C:\Users\adria\Python\python.exe -m morph_kgc $file
	year=${file:3:4}
	out_nt="out_cf_"$year"_v3.nt"
	echo "NT file generated: $out_nt"
	mv $out_nt graphs/nt/"$out_nt"
	echo "Done!"
    fi
done
