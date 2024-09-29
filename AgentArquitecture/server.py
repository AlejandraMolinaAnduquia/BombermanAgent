import mesa
from mesa.visualization.ModularVisualization import ModularServer
from model import BomberManModel
from mesa.visualization.modules import CanvasGrid,ChartModule
from Controllers.fileLoad import FileLoad
from numberAgent import NumberAgent

NUMBER_OF_CELLS=3
SIZE_OF_CANVAS_IN_PIXELS_X=500
SIZE_OF_CANVAS_IN_PIXELS_Y=500


fileLoad = FileLoad()
matrizArchivo = fileLoad.cargar_matriz_desde_archivo("mapa4.txt")
NumberCellsX=len(matrizArchivo[0])
NumberCellsY=len(matrizArchivo)

            
simulation_params={
    "number_of_agents":mesa.visualization.Slider(name='Number of Agents', value=1, min_value=1, max_value=200, step=1, description="seleccionar numero de agentes"),
    "width":NumberCellsX,
    "height":NumberCellsY,
}

def agent_portrayal(agent):
    
    portrayal = {"Shape": "circle","Filled:": "true","r": 0.5}
    if isinstance(agent, RobotAgent):
        return {"Shape":"iconos/robot.png", "Layer": 1, "scale": True}
    if isinstance(agent, WallAgent):
        return {"Shape":"iconos/muro.png", "Layer": 0, "scale": True} 
    if isinstance(agent, GoalAgent):
        return {"Shape":"iconos/bandera.png", "Layer": 0, "scale": True}
    if isinstance(agent, PackageAgent):
        return {"Shape":"iconos/paquete.png", "Layer": 1, "scale": True}
    if isinstance(agent, RoadAgent):
        return {"Shape":"iconos/pavimentacion.png", "Layer": 0, "scale": True}
    if isinstance(agent, NumberAgent):
        return {"Shape": "rect", 
                 "Filled": "true", 
                 "Layer": 2, 
                 "w": 10,
                 "h": 10,
                 "Color": "white",  # color de la celda
                 "text":str(agent.numero),
                 "expansion": str(agent.numero),  # número a mostrar
                 "text_color": "black"}

    return portrayal


grid=CanvasGrid(agent_portrayal,NumberCellsX,NumberCellsY,SIZE_OF_CANVAS_IN_PIXELS_X,SIZE_OF_CANVAS_IN_PIXELS_Y)

server=mesa.visualization.ModularServer(BomberManAgent,[grid],"BomberMan",model_params=simulation_params)
server.port=8521
server.launch()