import os
import sys
# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
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
        portrayal["Text"] = "Salida"
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
    temp_model = MazeModel(width=7, height=4, num_bombermans=1, num_comodines=0, mapa_filename=mapa_filename)
    return temp_model.contar_rocas()

# Cargar el número de rocas del mapa seleccionado
mapa_filename = "Data/Maps/mapa3.txt"
max_comodines = contar_rocas_en_mapa(mapa_filename)

# Crear la grilla donde se representarán los agentes
grid = CanvasGrid(agent_portrayal, 7, 4, 500, 500)



# Definir un nuevo TextElement para mostrar la lista de celdas visitadas y la pila
class DFSStateElement(TextElement):
    def render(self, model):
        bomberman = next(agent for agent in model.schedule.agents if isinstance(agent, Bomberman))
        visited = list(bomberman.visited)
        stack = bomberman.stack
        
        # Mostrar la información en formato legible
        return f"Visitados: {visited}\nPila: {stack}"
    

# Agregar el nuevo módulo TextElement para la visualización de la lista de celdas visitadas y la pila
dfs_state_element = DFSStateElement()

# Configurar el servidor para incluir la nueva visualización y selección de algoritmo
server = ModularServer(
    MazeModel,
    [grid, dfs_state_element],
    "Bomberman Maze",
    {
        "width": 7,
        "height": 4,
        "num_bombermans": Slider("Número de Bombermans", 1, 1, 5, 1),
        "num_comodines": Slider("Número de Comodines", 1, 1, max_comodines - 1, 1),
        "mapa_filename": mapa_filename
    }
)

server.port = 8521
server.launch()
