import os
import sys
# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice  # Importar Choice para el botón desplegable
from mesa.visualization.UserParam import Slider  # Importar Slider para la interfaz
from model import *


def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, Roca):
        portrayal["Shape"] = "Data/imagenes/roca.jpg"  # Ruta a la imagen de la roca
        portrayal["scale"] = 1  # Escala de la imagen
        portrayal["Layer"] = 1

    elif isinstance(agent, RocaSalida):
        portrayal["Shape"] = "Data/imagenes/salida.jpg"  # Imagen de la roca con salida
        portrayal["scale"] = 1
        portrayal["Text"] = "Salida"
        portrayal["Layer"] = 1

    elif isinstance(agent, Metal):
        portrayal["Shape"] = "Data/imagenes/muro.jpg"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif isinstance(agent, Bomberman):
        portrayal["Shape"] = "Data/imagenes/bomberman.jpg"  # Imagen de Bomberman
        portrayal["scale"] = 1
        portrayal["Layer"] = 2

    elif isinstance(agent, Bomba):
        portrayal["Shape"] = "Data/imagenes/bomba.jpg"  # Imagen de la bomba
        portrayal["scale"] = 0.8
        portrayal["Layer"] = 3

    elif isinstance(agent, Comodin):
        portrayal["Shape"] = "Data/imagenes/fuego.png"  # Imagen de animación
        portrayal["scale"] = 0.5
        portrayal["Layer"] = 2

    elif isinstance(agent, Explosion):
        portrayal["Shape"] = "Data/imagenes/explosion.png"  # Imagen de explosión
        portrayal["scale"] = 1
        portrayal["Layer"] = 4

    return portrayal

# Leer el tamaño del mapa desde el archivo de mapa
def obtener_dimensiones_mapa(mapa_filename):
    with open(mapa_filename, 'r') as f:
        mapa = [line.strip().split(',') for line in f.readlines()]
    height = len(mapa)
    width = len(mapa[0]) if height > 0 else 0
    return width, height

# Crear un modelo temporal para contar las rocas del mapa
def contar_rocas_en_mapa(mapa_filename):
    width, height = obtener_dimensiones_mapa(mapa_filename)
    temp_model = MazeModel(width=width, height=height, num_bombermans=1, num_comodines=0, mapa_filename=mapa_filename, recorrido_tipo=None)
    return temp_model.contar_rocas(), width, height

# Cargar el número de rocas del mapa seleccionado y las dimensiones
mapa_filename = "Data/Maps/mapa1.txt"
max_comodines, width, height = contar_rocas_en_mapa(mapa_filename)

# Crear el menú desplegable con las opciones para el tipo de recorrido
recorrido_selector = Choice(
    "Algoritmo de recorrido", 
    value="Anchura (BFS)",  # Opción por defecto
    choices=["Anchura (BFS)", "Profundidad (DFS)", "Costo uniforme"]
)

# Crear la grilla donde se representarán los agentes, usando las dimensiones del mapa
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

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
        "width": width,
        "height": height,
        "num_bombermans": Slider("Número de Bombermans", 1, 1, 5, 1),
        "num_comodines": Slider("Número de Comodines", 1, 1, max_comodines - 1, 1),
        "mapa_filename": mapa_filename,
        "recorrido_tipo": recorrido_selector
    }
)

server.port = 8521
server.launch()
