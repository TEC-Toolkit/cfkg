@echo off

echo Remember to install and activate morph-kgc

for %%f in (cf_*_v3.ini) do (
    if exist "%%f" (
        echo Dealing with %%f
        C:\Users\adria\Python\python.exe -m morph_kgc %%f
        set "year=%%~nf"
        set "year=!year:~3,4!"
        set "out_nt=out_cf_!year!_v3.nt"
        echo NT file generated: !out_nt!
        move !out_nt! graphs\nt\!out_nt!
        echo Done!
    )
)
