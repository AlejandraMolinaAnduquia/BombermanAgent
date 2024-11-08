from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization import Choice
from mesa.visualization.UserParam import Slider  

# Importaciones de agentes específicos de AgentArquitecture
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent
from AgentArquitecture.powerup import PowerupAgent
from AgentArquitecture.explosion import ExplosionAgent

from ModelArquitecture.model import MazeModel

def agent_portrayal(agent):
    """
    Define cómo se representará visualmente cada tipo de agente en la simulación.

    Args:
        agent (Agent): El agente a representar.

    Returns:
        dict: Diccionario con las propiedades visuales del agente.
    """
    if agent is None:
        return

    # Configuración básica de la visualización
    portrayal = {
        "w": 1, 
        "h": 1, 
        "Filled": "true",
    }

    # Especifica la representación visual según el tipo de agente
    if type(agent) is BombermanAgent:
        portrayal["Shape"] = "Data/Images/bomberman.png"
        portrayal["Layer"] = 1

    elif type(agent) is GoalAgent:
        if agent.visit_order:  # Muestra el orden de visita en texto
            portrayal["text"] = str(agent.visit_order)
            portrayal["text_color"] = "black" 
        portrayal["Shape"] = "Data/Images/salida.jpg"
        portrayal["Layer"] = 0

    elif type(agent) is MetalAgent:
        portrayal["Shape"] = "Data/Images/metal.jpg"
        portrayal["Color"] = "gray"
        portrayal["r"] = 1
        portrayal["Layer"] = 1

    elif type(agent) is RoadAgent:
        # Muestra el orden de visita y cambia el color si es parte del camino óptimo
        if agent.visit_order:
            portrayal["text"] = str(agent.visit_order)
            portrayal["text_color"] = "black" 
        portrayal["Color"] = "yellow" if agent.is_visited else "green"
        portrayal["Shape"] = "rect"
        portrayal["r"] = 1
        portrayal["Layer"] = 0

    elif type(agent) is RockAgent:
        if agent.visit_order:  # Muestra el orden de visita en texto
            portrayal["text"] = str(agent.visit_order)
            portrayal["text_color"] = "black" 
        portrayal["Shape"] = "Data/Images/roca.jpg"
        portrayal["Color"] = "firebrick"
        portrayal["r"] = 1
        portrayal["Layer"] = 0

    elif type(agent) is GlobeAgent:
        portrayal["Shape"] = "Data/Images/globe.png"
        portrayal["Layer"] = 1

    elif type(agent) is BombAgent:
        portrayal["Shape"] = "Data/Images/bomba.png"
        portrayal["Layer"] = 1

    elif type(agent) is PowerupAgent:
        if agent.original_visit_order:
            portrayal["text"] = str(agent.original_visit_order)
            portrayal["text_color"] = "black" 
        portrayal["Shape"] = "Data/Images/fuego.png"
        portrayal["Layer"] = 0

    elif isinstance(agent, ExplosionAgent):
        portrayal["Shape"] = "Data/Images/explosion.png"
        portrayal["Layer"] = 2

    return portrayal


def create_server(map):
    """
    Crea el servidor de la simulación usando la biblioteca `mesa`.

    Args:
        map (list of list): Mapa de la simulación, especificando los tipos de celdas.

    Returns:
        ModularServer: El servidor configurado para la simulación.
    """
    # Dimensiones del mapa

    height = len(map)
    width = len(map[0])
    grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

    params = {
        "height": height,
        "width": width,
        "map": map,
        "search_strategy": Choice(
            "Recorridos",
            value="A*",
            choices=["BFS", "DFS", "UCS", "A*", "Beam Search", "Hill Climbing"], 
        ),
        "distance_metric": Choice(  # Nuevo parámetro para seleccionar la distancia
            "Métrica de Distancia",
            value="Manhattan",
            choices=["Manhattan", "Euclidean"],
        ),
        "beta": Slider("Beta", value=2, min_value=1, max_value=2),
    }

    
    # Crea el servidor de la simulación con el modelo, grilla y parámetros
    server = ModularServer(MazeModel, [grid], "Bomberman", params)
    server.port = 8521
    return server
