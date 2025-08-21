import pandas as pd
import matplotlib.pyplot as plt

def limpiar_pantalla():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def filtrar_datos(df):
    """Permite al usuario filtrar los datos por zona, empresa y fecha."""
    df_filtrado = df.copy()
    
    print("\n--- Filtro de Datos ---")
    
    # Filtrar por Zona
    zonas_disponibles = df_filtrado['ZONA'].unique()
    print(f"Zonas disponibles: {list(zonas_disponibles)}")
    zonas = input("Filtra por ZONA (deja en blanco para no filtrar, separa por comas para varias): ")
    if zonas:
        df_filtrado = df_filtrado[df_filtrado['ZONA'].isin([z.strip() for z in zonas.split(',')])]

    # Filtrar por Empresa
    empresas_disponibles = df_filtrado['EMPRESA'].unique()
    print(f"\nEmpresas disponibles: {list(empresas_disponibles)}")
    empresas = input("Filtra por EMPRESA (deja en blanco para no filtrar, separa por comas para varias): ")
    if empresas:
        df_filtrado = df_filtrado[df_filtrado['EMPRESA'].isin([e.strip() for e in empresas.split(',')])]

    # Filtrar por Fecha
    print("\nFiltrar por rango de fechas (formato YYYY-MM-DD):")
    fecha_inicio = input("Fecha de inicio (deja en blanco para no filtrar): ")
    fecha_fin = input("Fecha de fin (deja en blanco para no filtrar): ")
    if fecha_inicio and fecha_fin:
        df_filtrado = df_filtrado[(df_filtrado['FE_APERTURA'] >= pd.to_datetime(fecha_inicio)) & (df_filtrado['FE_APERTURA'] <= pd.to_datetime(fecha_fin))]
    
    print(f"\n{len(df_filtrado)} registros encontrados tras aplicar los filtros.")
    return df_filtrado

def mostrar_tabla(df):
    """Muestra los datos en formato de tabla en la consola."""
    if df.empty:
        print("No hay datos para mostrar.")
        return
    print("\n--- Tabla de Datos ---")
    print(df)

def grafico_por_zona(df):
    """Genera un gráfico de barras de casos por zona."""
    if df.empty:
        print("No hay datos para generar el gráfico.")
        return
    
    plt.figure(figsize=(10, 6))
    df['ZONA'].value_counts().plot(kind='bar', color='skyblue')
    plt.title('Cantidad de Casos por Zona')
    plt.xlabel('Zona')
    plt.ylabel('Cantidad de Casos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('grafico_zona.png')
    print("\nGráfico 'grafico_zona.png' generado exitosamente.")

def grafico_por_empresa(df):
    """Genera un gráfico de barras de casos por empresa."""
    if df.empty:
        print("No hay datos para generar el gráfico.")
        return

    plt.figure(figsize=(12, 7))
    df['EMPRESA'].value_counts().plot(kind='bar', color='lightgreen')
    plt.title('Cantidad de Casos por Empresa')
    plt.xlabel('Empresa')
    plt.ylabel('Cantidad de Casos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('grafico_empresa.png')
    print("\nGráfico 'grafico_empresa.png' generado exitosamente.")

def menu_resultados(df):
    """Muestra el menú de acciones para los datos filtrados."""
    while True:
        print("\n--- ¿Qué deseas hacer? ---")
        print("1. Mostrar tabla de datos")
        print("2. Generar gráfico por Zona")
        print("3. Generar gráfico por Empresa")
        print("4. Volver al menú principal")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            mostrar_tabla(df)
        elif opcion == '2':
            grafico_por_zona(df)
        elif opcion == '3':
            grafico_por_empresa(df)
        elif opcion == '4':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")
        input("\nPresiona Enter para continuar...")
        limpiar_pantalla()
        print(f"{len(df)} registros en memoria.")

def main():
    """Función principal del script interactivo."""
    archivo_excel = 'Detalle de Casos Abiertos Técnica Sucursal (19-08-2025).xlsx'
    try:
        # Lee el archivo de Excel, especificando que la fila 6 es el encabezado (índice 5)
        df_original = pd.read_excel(archivo_excel, header=5)
        df_original['FE_APERTURA'] = pd.to_datetime(df_original['FE_APERTURA'])
        print(f"Archivo '{archivo_excel}' cargado exitosamente.")
        print(f"Se encontraron {len(df_original)} registros.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_excel}'")
        return
    except KeyError as e:
        print(f"Error: No se encontró la columna {e} en el archivo de Excel.")
        return
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar el archivo: {e}")
        return

    df_actual = df_original.copy()

    while True:
        limpiar_pantalla()
        print("--- Menú Principal ---")
        print(f"Actualmente hay {len(df_actual)} registros cargados.")
        print("1. Aplicar filtros")
        print("2. Ver resultados (con datos actuales)")
        print("3. Resetear filtros")
        print("4. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            df_actual = filtrar_datos(df_original)
            menu_resultados(df_actual)
        elif opcion == '2':
            menu_resultados(df_actual)
        elif opcion == '3':
            df_actual = df_original.copy()
            print("Filtros reseteados.")
        elif opcion == '4':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")
        input("\nPresiona Enter para continuar...")

if __name__ == '__main__':
    main()