import os
import sys
# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider  # Importar Slider para la interfaz
from model import *

def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Color": "blue", "r": 0.8, "Layer": 1}
    
    if isinstance(agent, Roca):
        portrayal["Color"] = "green"
    elif isinstance(agent, RocaSalida):
        portrayal["Color"] = "red"
    elif isinstance(agent, Metal):
        portrayal["Color"] = "black"
    elif isinstance(agent, Bomberman):
        portrayal["Color"] = "blue"
    elif isinstance(agent, Bomba):  # Mostrar la bomba
        portrayal["Color"] = "yellow"
    elif isinstance(agent, Comodin):  # Mostrar los comodines
        portrayal["Color"] = "orange"

    return portrayal

# Crear un modelo temporal para contar las rocas del mapa
def contar_rocas_en_mapa(mapa_filename):
    temp_model = MazeModel(width=7, height=4, num_bombermans=1, num_comodines=0, mapa_filename=mapa_filename)
    return temp_model.contar_rocas()

# Cargar el número de rocas del mapa seleccionado
mapa_filename = "Data/Maps/mapa1.txt"
max_comodines = contar_rocas_en_mapa(mapa_filename)

grid = CanvasGrid(agent_portrayal, 7, 4, 500, 500)

# Crear sliders dinámicamente después de contar las rocas
server = ModularServer(
    MazeModel,
    [grid],
    "Bomberman Maze",
    {
        "width": 7,
        "height": 4,
        "num_bombermans": Slider("Número de Bombermans", 1, 1, 5, 1),  # Slider para elegir el número de Bombermans
        "num_comodines": Slider("Número de Comodines", 1, 1, max_comodines, 1),  # Slider dinámico basado en las rocas
        "mapa_filename": mapa_filename
    }
)

server.port = 8521

server.launch()