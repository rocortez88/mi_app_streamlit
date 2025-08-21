
import pandas as pd

def verificar_columnas(archivo_excel):
    """Lee la primera fila de un archivo Excel y muestra los nombres de las columnas."""
    try:
        # Leemos solo la primera fila para obtener los encabezados de manera eficiente
        df_encabezados = pd.read_excel(archivo_excel, nrows=0)
        print("Los nombres de las columnas en tu archivo son:")
        print(list(df_encabezados.columns))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_excel}'")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    archivo_entrada = 'Detalle de Casos Abiertos Técnica Sucursal (19-08-2025).xlsx'
    verificar_columnas(archivo_entrada)
