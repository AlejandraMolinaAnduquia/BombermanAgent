from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization import Choice
from mesa.visualization.UserParam import Slider  

# Import AgentArquitecture
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent  # Importar BombAgent
from AgentArquitecture.powerup import PowerupAgent  # Importar PowerupAgent
from AgentArquitecture.explosion import ExplosionAgent  # Importar ExplosionAgent

from ModelArquitecture.model import MazeModel

def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "w": 1, 
        "h": 1, 
        "Filled": "true",
    }

    if type(agent) is BombermanAgent:
        portrayal["Shape"] = "Data/Images/bomberman.jpg"
        portrayal["Layer"] = 1
    elif type(agent) is GoalAgent:
        portrayal["Shape"] = "Data/Images/salida.jpg"
        portrayal["Layer"] = 0
    elif type(agent) is MetalAgent:
        portrayal["Shape"] = "Data/Images/muro.jpg"
        portrayal["Color"] = "gray"
        portrayal["r"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is RoadAgent:
        if agent.visit_order:
            portrayal["text"] = str(agent.visit_order)
            portrayal["text_color"] = "black" 
        if agent.is_visited:
            portrayal["Color"] = "yellow"
        else:
            portrayal["Color"] = "green"
        portrayal["Shape"] = "rect"
        portrayal["r"] = 1
        portrayal["Layer"] = 0
    elif type(agent) is RockAgent:
        portrayal["Shape"] = "Data/Images/roca.jpg"
        portrayal["Color"] = "firebrick"
        portrayal["r"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is GlobeAgent:
        portrayal["Shape"] = "Data/Images/globo.png"
        portrayal["Layer"] = 1
    elif type(agent) is BombAgent:  # Añadir condición para BombAgent
        portrayal["Shape"] = "Data/Images/bomba.jpg"
        portrayal["Layer"] = 1
    elif type(agent) is PowerupAgent:  # Añadir condición para PowerupAgent
        portrayal["Shape"] = "Data/Images/fuego.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, ExplosionAgent):  # Representación visual del agente de explosión
        portrayal["Color"] = "red"
        portrayal["Shape"] = "rect"
        portrayal["Layer"] = 2

    return portrayal

def create_server(map):
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
            choices=["BFS", "DFS", "UCS", "A*"],
        )
    }

    server = ModularServer(MazeModel, [grid], "Bomberman", params)
    server.port = 8521
    return server