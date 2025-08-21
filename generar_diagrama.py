
from diagrams import Diagram, Cluster, Edge, Node

# El nombre del archivo de salida terminará en .gv (Graphviz)
output_filename = "diagrama_para_importar"

with Diagram("Flujo de la Aplicación de Análisis", show=False, direction="TB", outformat="dot", filename=output_filename) as diag:

    # Usaremos nodos genéricos para máxima compatibilidad
    excel_file = Node("Fuente de Datos\n(Excel)", shape="cylinder", style="filled", fillcolor="lightgreen")

    with Cluster("App Streamlit (app_streamlit.py)"):
        app_entry = Node("Inicio de la App\n(Streamlit)", shape="box", style="filled", fillcolor="lightblue")

        with Cluster("Barra Lateral de Filtros"):
            filtros = Node("Controles Interactivos\n(Checkboxes, Selectores)", shape="box3d")

        with Cluster("Página Principal (Contenido Dinámico)"):
            metricas = Node("Métrica: Total de Casos", shape="oval")
            tabla_detalle = Node("Tabla de Detalle de Casos", shape="note")
            
            with Cluster("Secciones de Análisis"):
                graficos = Node("Gráficos de Barras", shape="component")
                tabla_resumen = Node("Tabla Resumen\n(Zona y Fecha)", shape="note")
                tabla_caja = Node("Tabla Cajas Repetidas", shape="note")
                tabla_finalizadas = Node("Tabla Tareas Finalizadas", shape="note")
                
                # Conexiones internas de la página
                metricas >> tabla_detalle >> graficos >> tabla_resumen >> tabla_caja >> tabla_finalizadas

    # Flujo general
    excel_file >> app_entry >> filtros >> metricas

diag

print(f"\nArchivo '{output_filename}.gv' generado exitosamente.")
print("Este es el archivo que debes importar en app.diagrams.net.")
