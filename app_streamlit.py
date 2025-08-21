import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import glob
import os

# --- Funciones de Lógica ---

def mapear_ciudad(zona):
    """
    Agrupa los valores de la columna 'ZONA' en un nombre de ciudad simplificado.
    """
    zona_limpia = str(zona).strip()

    zonas_guayaquil = [
        "AURORA GYE", "CENTRO SUR GYE", "CENTRO SUR,Duran,N/A",
        "CENTRO SUR GYE, N/A", "Duran", "INMACONSA 2 GYE",
        "INMACONSA 2 GYE,INMACONSA GYE", "INMACONSA GYE", "KENNEDY GYE",
        "KENNEDY GYE,N/A", "N/A,SUR 1 GYE", "SUR 1 GYE",
        "SUR 1 GYE.SUR 2 GYE", "SUR 2 GYE", "MIRAFLORES GYE"
    ]
    
    zonas_quito = [
        "ARMENIA UIO", "BORROMONI UIO", "COTOCOLLAO UIO", "GOSSEAL UIO",
        "MUROS UIO", "N/A,ZONA INDUSTRIAL UIO", "SUR 2 UIO", "ZONA INDUSTRIAL UIO"
    ]

    if zona_limpia in zonas_guayaquil:
        return "Guayaquil"
    elif zona_limpia in zonas_quito:
        return "Quito"
    
    # De lo contrario, devuelve el nombre original de la zona.
    return zona_limpia

@st.cache_data
def cargar_datos():
    """
    Carga datos del Excel, los limpia y añade la columna 'CIUDAD'.
    """
    try:
        folder_path = os.getcwd()
        file_pattern = "Detalle de Casos Abiertos Técnica Sucursal*.xlsx"
        full_pattern = os.path.join(folder_path, file_pattern)
        list_of_files = glob.glob(full_pattern)
        
        if not list_of_files:
            st.error(f"Error: No se encontró archivo que coincida con '{file_pattern}'.")
            return None
        
        excel_file_path = list_of_files[0]
        st.info(f"Cargando datos desde: {os.path.basename(excel_file_path)}")

        df = pd.read_excel(excel_file_path, header=5)
        
        # Limpieza de columnas de texto
        for col in ['ZONA', 'EMPRESA', 'AFECTADOS', 'NUMERO_CASO', 'CAJA', 'ESTADO_CASO', 'ESTADO_TAREA', 'OLT_SW']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        df['FE_APERTURA'] = pd.to_datetime(df['FE_APERTURA'])
        
        # --- Creación de la nueva columna CIUDAD ---
        if 'ZONA' in df.columns:
            df['CIUDAD'] = df['ZONA'].apply(mapear_ciudad)
        else:
            st.error("La columna 'ZONA' es necesaria para el mapeo de ciudades y no fue encontrada.")
            return None
            
        return df
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al leer el archivo: {e}")
        return None

# --- Configuración de la App Streamlit ---

st.set_page_config(layout="wide", page_title="Análisis de Casos")
st.title('📊 Analizador Interactivo de Casos')

df_original = cargar_datos()

if df_original is not None:
    
    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header('Filtros')

    # Filtros especiales
    st.sidebar.markdown("**Filtros Especiales por Afectado**")
    filtro_mostrar = st.sidebar.checkbox('Mostrar solo afectados MIMG o TN_WIFI')
    filtro_omitir = st.sidebar.checkbox('Omitir afectados MIMG y TN_WIFI', disabled=filtro_mostrar)
    if filtro_mostrar:
        filtro_omitir = False 

    st.sidebar.divider()

    # Filtros generales
    st.sidebar.markdown("**Filtros Generales**")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Selección Rápida de Ciudad**")
    opcion_ciudad_rapida = st.sidebar.radio(
        "Elige una opción:",
        ("Todas las Ciudades/Zonas", "Solo Guayaquil", "Solo Quito")
    )

    ciudades_disponibles = sorted(df_original['CIUDAD'].unique())

    if opcion_ciudad_rapida == "Solo Guayaquil":
        default_ciudades = ["Guayaquil"]
        multiselect_disabled = True
    elif opcion_ciudad_rapida == "Solo Quito":
        default_ciudades = ["Quito"]
        multiselect_disabled = True
    else:
        default_ciudades = ciudades_disponibles
        multiselect_disabled = False

    ciudades_seleccionadas = st.sidebar.multiselect(
        'Selecciona Ciudades/Zonas:',
        ciudades_disponibles,
        default=default_ciudades,
        disabled=multiselect_disabled
    )

    if not ciudades_seleccionadas:
        ciudades_seleccionadas = ciudades_disponibles

    # Filtro por Empresa
    empresas_disponibles = sorted(df_original['EMPRESA'].unique())
    empresas_seleccionadas = st.sidebar.multiselect('Empresas', empresas_disponibles, default=empresas_disponibles)

    # Filtro por Fecha
    min_fecha = df_original['FE_APERTURA'].min().date()
    max_fecha = df_original['FE_APERTURA'].max().date()
    fecha_seleccionada = st.sidebar.date_input(
        'Rango de Fechas',
        value=(min_fecha, max_fecha),
        min_value=min_fecha,
        max_value=max_fecha,
        format="YYYY-MM-DD"
    )

    # Aplicar filtros al DataFrame
    if len(fecha_seleccionada) == 2:
        df_filtrado = df_original[
            (df_original['CIUDAD'].isin(ciudades_seleccionadas)) &
            (df_original['EMPRESA'].isin(empresas_seleccionadas)) &
            (df_original['FE_APERTURA'].dt.date >= fecha_seleccionada[0]) &
            (df_original['FE_APERTURA'].dt.date <= fecha_seleccionada[1])
        ]
    else:
        df_filtrado = pd.DataFrame()

    # Aplicar filtros especiales
    if 'AFECTADOS' in df_filtrado.columns:
        if filtro_mostrar:
            df_filtrado = df_filtrado[
                df_filtrado['AFECTADOS'].str.startswith('mimg', na=False) | 
                df_filtrado['AFECTADOS'].str.startswith('tn_wifi', na=False)
            ]
        elif filtro_omitir:
            df_filtrado = df_filtrado[~
                (df_filtrado['AFECTADOS'].str.startswith('mimg', na=False) | 
                 df_filtrado['AFECTADOS'].str.startswith('tn_wifi', na=False))
            ]
    
    # --- PÁGINA PRINCIPAL ---
    st.header('Resultados Filtrados')
    st.metric(label="Total de Casos Filtrados", value=f"{len(df_filtrado)}")
    st.subheader('Detalle de Casos')
    st.dataframe(df_filtrado)
    st.divider()

    # Gráficos
    st.subheader('Visualización de Datos Agrupados')
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Casos por Zona")
        if not df_filtrado.empty:
            fig, ax = plt.subplots()
            counts = df_filtrado['ZONA'].value_counts()
            counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_xlabel('Zona')
            ax.set_ylabel('Cantidad')
            plt.xticks(rotation=45, ha='right')
            for container in ax.containers:
                ax.bar_label(container)
            st.pyplot(fig)

    with col2:
        st.markdown("##### Casos por Empresa")
        if not df_filtrado.empty:
            fig, ax = plt.subplots()
            counts = df_filtrado['EMPRESA'].value_counts()
            counts.plot(kind='bar', ax=ax, color='lightgreen')
            ax.set_xlabel('Empresa')
            ax.set_ylabel('Cantidad')
            plt.xticks(rotation=45, ha='right')
            for container in ax.containers:
                ax.bar_label(container)
            st.pyplot(fig)

    st.divider()

    # Tabla dinámica
    st.subheader('Tabla Resumen: Casos por Zona y Fecha')
    if not df_filtrado.empty:
        df_pivot_data = df_filtrado.groupby([df_filtrado['FE_APERTURA'].dt.date, 'ZONA']).size().reset_index(name='count')
        tabla_resumen = df_pivot_data.pivot_table(index='ZONA', columns='FE_APERTURA', values='count', aggfunc='sum', fill_value=0)
        if not tabla_resumen.empty:
            tabla_resumen['Total'] = tabla_resumen.sum(axis=1)
        st.dataframe(tabla_resumen)

    st.divider()

    # Tabla de Casos con Caja Repetida
    st.subheader('Casos con Caja Repetida')
    if not df_filtrado.empty and 'NUMERO_CASO' in df_filtrado.columns and 'CAJA' in df_filtrado.columns:
        # Encontrar cajas que no son únicas (excluyendo valores nulos)
        cajas_no_nulas = df_filtrado.dropna(subset=['CAJA'])
        if not cajas_no_nulas.empty:
            cajas_duplicadas = cajas_no_nulas[cajas_no_nulas.duplicated(subset=['CAJA'], keep=False)]
            
            if not cajas_duplicadas.empty:
                # Mostrar solo las columnas relevantes, ordenadas por CAJA para agrupar visualmente
                st.dataframe(cajas_duplicadas[['NUMERO_CASO', 'CAJA']].sort_values(by='CAJA'))
            else:
                st.info("No se encontraron cajas repetidas en los datos filtrados.")
        else:
            st.info("No hay cajas para analizar en los datos filtrados.")
    else:
        st.info("No hay datos para mostrar o faltan las columnas 'NUMERO_CASO' o 'CAJA'.")

    st.divider()

    # Tabla de Tareas Finalizadas
    st.subheader('Tareas Finalizadas')
    required_cols = ['NUMERO_CASO', 'ESTADO_CASO', 'ESTADO_TAREA', 'OLT_SW']
    if not df_filtrado.empty and all(col in df_filtrado.columns for col in required_cols):
        # Filtrar por ESTADO_TAREA == 'Finalizada' (insensible a mayúsculas/minúsculas y espacios)
        finalizadas = df_filtrado[df_filtrado['ESTADO_TAREA'].str.strip().str.lower() == 'finalizada']
        
        if not finalizadas.empty:
            st.dataframe(finalizadas[required_cols])
        else:
            st.info("No se encontraron tareas finalizadas en los datos filtrados.")
    else:
        st.info("No hay datos para mostrar o faltan una o más columnas requeridas.")
