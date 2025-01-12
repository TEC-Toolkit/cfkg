@echo off

echo Remember to install and activate morph-kgc

REM Procesar los archivos .ini
for %%f in (cf_*_v3.ini) do (
    if exist "%%f" (
        echo Dealing with %%f
        C:\Users\adria\Python\python.exe -m morph_kgc %%f
        set "year=%%~nf"
        set "year=!year:~3,4!"
        set "out_nt=out_cf_!year!_v3.nt"
        echo NT file generated: !out_nt!
        move "!out_nt!" "graphs\v3\nt\!out_nt!"
        echo .nt Done!
    )
)

REM Ejecutar el script para limpiar archivos malformados
py malformacion_lineas_nt.py

REM Procesar los archivos .nt

@echo off
setlocal EnableDelayedExpansion

for %%f in (graphs\v3\nt\*.nt) do (
    if exist %%f (
        echo Dealing with %%f
        set "file_name=%%~nf"
        set "year=!file_name:~7,4!"  REM Leer el año desde la posición correcta
        set "out_ttl=graphs\v3\ttl\out_cf_!year!_v3.ttl"
        set "full_out_ttl=%cd%\!out_ttl!"  REM Obtener la ruta completa

        echo Generating TTL file: !out_ttl!
        py nt_to_ttl.py %%f "!full_out_ttl!"
        echo TTL file generated: !full_out_ttl!
        echo Output path: !full_out_ttl!
        echo .ttl Done!
    ) else (
        echo Error: %%f not found!
    )
)

endlocal