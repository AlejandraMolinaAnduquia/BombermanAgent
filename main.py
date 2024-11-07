import sys
from Utils.dinamicTools import load_map, get_map_path
from ServerArquitecture.server import create_server

if __name__ == "__main__":
    # Obtiene la ruta del archivo de mapa seleccionada por el usuario
    map_path = get_map_path()
    
    # Verifica si se seleccionó un archivo
    if map_path:
        # Carga el mapa desde el archivo seleccionado
        map = load_map(map_path)
        
        # Crea el servidor de simulación usando el mapa cargado
        server = create_server(map)
        
        # Lanza el servidor para iniciar la simulación
        server.launch()
    else:
        # Muestra un mensaje de error si no se seleccionó un archivo
        print("No file selected.")
        
        # Finaliza el programa con código de salida 0 (error)
        sys.exit(0)
