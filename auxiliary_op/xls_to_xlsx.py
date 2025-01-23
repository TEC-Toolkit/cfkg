import os
import win32com.client as win32

# Directorio que contiene los archivos .xls
directorio = r"C:\Users\adria\TFG\cfkg\BEIS-UK\data_raw"

# Inicializar Excel
excel = win32.gencache.EnsureDispatch('Excel.Application')
excel.Visible = False  # No mostrar la aplicación Excel

# Recorre todos los archivos en el directorio
for archivo in os.listdir(directorio):
    if archivo.endswith('.xls'):
        ruta_xls = os.path.join(directorio, archivo)
        ruta_xlsx = os.path.join(directorio, archivo.replace('.xls', '.xlsx'))

        # Abre el archivo .xls
        workbook = excel.Workbooks.Open(ruta_xls)

        # Guarda el archivo como .xlsx
        workbook.SaveAs(ruta_xlsx, FileFormat=51)  # 51 es el formato para .xlsx
        workbook.Close()
        print(f"Convertido: {archivo} a formato .xlsx")

# Cerrar Excel
excel.Application.Quit()
print("Conversión completa")
