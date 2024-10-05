import os
import sys
# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice  # Importar Choice para el botón desplegable
from mesa.visualization.UserParam import Slider  # Importar Slider para la interfaz
from model import *


def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, Roca):
        portrayal["Shape"] = "Data/imagenes/roca.png"  # Ruta a la imagen de la roca
        portrayal["scale"] = 1  # Escala de la imagen
        portrayal["Layer"] = 1

    elif isinstance(agent, RocaSalida):
        portrayal["Shape"] = "Data/imagenes/salida.png"  # Imagen de la roca con salida
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif isinstance(agent, Metal):
        portrayal["Shape"] = "Data/imagenes/metal.jpg"  # Imagen de metal
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif isinstance(agent, Bomberman):
        portrayal["Shape"] = "Data/imagenes/bomberman.png"  # Imagen de Bomberman
        portrayal["scale"] = 1
        portrayal["Layer"] = 2

    elif isinstance(agent, Bomba):
        portrayal["Shape"] = "Data/imagenes/bomba.jpg"  # Imagen de la bomba
        portrayal["scale"] = 0.8
        portrayal["Layer"] = 3

    elif isinstance(agent, Comodin):
        portrayal["Shape"] = "Data/imagenes/fuego.png"  # Imagen de comodín
        portrayal["scale"] = 0.5
        portrayal["Layer"] = 2

    elif isinstance(agent, Explosion):
        portrayal["Shape"] = "Data/imagenes/explosion.png"  # Imagen de explosión
        portrayal["scale"] = 1
        portrayal["Layer"] = 4

    return portrayal

# Crear un modelo temporal para contar las rocas del mapa
def contar_rocas_en_mapa(mapa_filename):
    temp_model = MazeModel(width=7, height=4, num_bombermans=1, num_comodines=0, mapa_filename=mapa_filename, recorrido_tipo=None)
    return temp_model.contar_rocas()

# Cargar el número de rocas del mapa seleccionado
mapa_filename = "Data/Maps/mapa3.txt"
max_comodines = contar_rocas_en_mapa(mapa_filename)

# Crear el menú desplegable con las opciones para el tipo de recorrido
recorrido_selector = Choice(
    "Algoritmo de recorrido", 
    value="Anchura (BFS)",  # Opción por defecto
    choices=["Anchura (BFS)", "Profundidad (DFS)", "Costo uniforme"]
)

# Crear la grilla donde se representarán los agentes
grid = CanvasGrid(agent_portrayal, 7, 4, 500, 500)

# Configurar el servidor con sliders dinámicos basados en el número de rocas
server = ModularServer(
    MazeModel,
    [grid],
    "Bomberman Maze",
    {
        "width": 7,
        "height": 4,
        "num_bombermans": Slider("Número de Bombermans", 1, 1, 5, 1),
        "num_comodines": Slider("Número de Comodines", 1, 1, max_comodines-1, 1),
        "mapa_filename": mapa_filename,
        "recorrido_tipo": recorrido_selector
    }
)

server.port = 8521
server.launch()
