import os
import sys

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
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

    return portrayal

grid = CanvasGrid(agent_portrayal, 7, 4, 500, 500)

server = ModularServer(MazeModel,
                       [grid],
                       "Bomberman Maze",
                       {"width": 7, "height": 4, "num_bombermans": 1, "num_comodines": 3, "mapa_filename": "Data\Maps\mapa1.txt"})

server.port = 8521
server.launch()
